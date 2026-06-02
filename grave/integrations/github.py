"""GitHub integration via the gh CLI subprocess boundary.

Wraps ``gh search repos`` and ``gh api repos/{owner}/{repo}``. All subprocess
invocations funnel through :func:`_run_gh`, which adds a timeout and a single
retry on transient failures. Errors are raised as typed :class:`GhError`
subclasses carrying user-facing messages; this module never prints. The CLI
dispatch layer is responsible for rendering those messages and choosing an
exit code.
"""

from __future__ import annotations

import json
import re
import subprocess
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from grave.models.repo import RepoItem
    from grave.models.search import SearchSpec


__all__ = [
    "GhAuthError",
    "GhError",
    "GhNotFoundError",
    "GhNotInstalledError",
    "GhRateLimitError",
    "GhTimeoutError",
    "check_gh_auth",
    "get_repo",
    "search_repos",
]


class GhError(RuntimeError):
    """Base class for all gh CLI failures. Its message is user-facing."""


class GhNotInstalledError(GhError):
    """The gh CLI executable could not be found on PATH."""


class GhAuthError(GhError):
    """gh is installed but not authenticated against GitHub."""


class GhRateLimitError(GhError):
    """The GitHub API rejected the request for exceeding the rate limit."""


class GhNotFoundError(GhError):
    """A requested repository does not exist."""


class GhTimeoutError(GhError):
    """A gh invocation did not complete within the allotted time."""


_JSON_FIELDS = (
    "fullName,description,stargazersCount,forksCount,watchersCount,"
    "openIssuesCount,language,createdAt,pushedAt,updatedAt,url"
)

# Search qualifiers map 1:1 to gh flags except `pushed`, which gh exposes as
# `--updated` (its last-push abandonment filter). Anything else is `--{name}`.
QUALIFIER_FLAGS = {"pushed": "--updated"}

_VALID_SORTS = frozenset({"stars", "forks", "updated"})
_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def _invoke_gh(args: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    """Run gh once, translating both unrecoverable cases into typed GhErrors.

    Timeout and transient OSError propagate raw so :func:`_run_gh` can decide
    whether to retry; a missing executable raises immediately (retry is futile).
    """
    try:
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except FileNotFoundError as e:
        # gh is not installed at all — retrying cannot help.
        raise GhNotInstalledError("gh CLI not found. Install it: https://cli.github.com") from e


def _run_gh(args: list[str], *, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    """Run a gh command, retrying once on timeout or transient OS/network errors.

    Never retries rate-limit failures (those surface from returncode inspection,
    not from this call). A timeout or transient OSError is retried exactly once;
    a second failure raises a typed GhError. Every path returns or raises, so no
    variable is left possibly-unbound.
    """
    try:
        return _invoke_gh(args, timeout)
    except (subprocess.TimeoutExpired, OSError):
        # First attempt failed transiently; retry exactly once.
        try:
            return _invoke_gh(args, timeout)
        except subprocess.TimeoutExpired as e:
            raise GhTimeoutError(f"gh CLI timed out after {timeout}s. Try again later.") from e
        except OSError as e:
            raise GhError(f"gh CLI failed to run: {e}") from e


def check_gh_auth() -> None:
    """Verify that gh is installed and authenticated.

    Returns None on success.

    Raises:
        GhNotInstalledError: If the gh executable is missing.
        GhAuthError: If gh is installed but not authenticated.
    """
    result = _run_gh(["gh", "auth", "status"])
    if result.returncode != 0:
        raise GhAuthError(
            "GitHub authentication required. Run 'gh auth login' (or 'grave init' to set up)."
        )


def _merge_sort_key(sort: str | None) -> Callable[[RepoItem], int | str]:
    """Return a key function for merge-sorting multi-keyword results client-side.

    Numeric keys return their int directly (0 sorts last under reverse=True);
    the date key is a string. Mixing an `or ""` fallback into the numeric keys
    would coerce a legitimate 0 to "" and break the sort with a str/int compare.
    Defaults to stars.
    """
    if sort == "updated":
        return lambda r: r["updated_at"]
    if sort == "forks":
        return lambda r: r["forks_count"]
    return lambda r: r["stargazers_count"]


def _normalize_item(item: dict[str, Any]) -> RepoItem:
    """Convert gh CLI JSON field names to snake_case GitHub API format.

    Missing language/description normalize to None (not "") so empty values
    stay falsy and never surface as blank rows in stats or exports.
    """
    return {
        "full_name": item.get("fullName", ""),
        "description": item.get("description") or None,
        "stargazers_count": item.get("stargazersCount", 0),
        "forks_count": item.get("forksCount", 0),
        "watchers_count": item.get("watchersCount", 0),
        "open_issues_count": item.get("openIssuesCount", 0),
        "language": item.get("language") or None,
        "created_at": item.get("createdAt", ""),
        "pushed_at": item.get("pushedAt", ""),
        "updated_at": item.get("updatedAt", ""),
        "topics": [],
        "html_url": item.get("url", ""),
    }


def _raise_for_gh_error(stderr: str, returncode: int, *, not_found: str | None = None) -> None:
    """Translate a failed gh invocation into the appropriate typed GhError."""
    lowered = stderr.lower()
    if "gh: command not found" in stderr:
        raise GhNotInstalledError("gh CLI not found. Install it: https://cli.github.com")
    if "authentication" in lowered or "401" in stderr:
        raise GhAuthError("GitHub authentication required. Run: gh auth login")
    if not_found is not None and ("404" in stderr or "not found" in lowered):
        raise GhNotFoundError(f"Repository not found: {not_found}")
    if "rate limit" in lowered or "403" in stderr:
        raise GhRateLimitError("GitHub API rate limit exceeded. Try again later.")
    raise GhError(f"gh CLI failed with exit code {returncode}: {stderr}")


def _run_repo_search(cmd: list[str]) -> list[RepoItem]:
    """Run one `gh search repos` invocation and return normalized items."""
    result = _run_gh(cmd)
    if result.returncode != 0:
        _raise_for_gh_error(result.stderr.strip(), result.returncode)
    try:
        items = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise GhError(f"Invalid JSON response from GitHub API: {e}") from e
    return [_normalize_item(item) for item in items]


def _multi_keyword_search(
    base_cmd: list[str],
    keywords: list[str],
    per_kw_limit: int,
    total_limit: int,
    sort: str | None,
) -> dict[str, list[RepoItem]]:
    """Search each keyword separately and merge results, deduped by full_name."""
    seen: set[str] = set()
    merged: list[RepoItem] = []
    for keyword in keywords:
        cmd = [*base_cmd, keyword]
        if sort:
            cmd.extend(["--sort", sort, "--order", "desc"])
        cmd.extend(["--limit", str(per_kw_limit), "--json", _JSON_FIELDS])
        for item in _run_repo_search(cmd):
            name = item["full_name"]
            if name not in seen:
                seen.add(name)
                merged.append(item)

    merged.sort(key=_merge_sort_key(sort), reverse=True)
    return {"items": merged[:total_limit]}


def search_repos(
    spec: SearchSpec, limit: int = 30, sort: str | None = None
) -> dict[str, list[RepoItem]]:
    """Search GitHub repositories using gh CLI.

    Args:
        spec: Structured search with keywords and qualifiers kept separate
        limit: Maximum number of results to return (must be > 0)
        sort: Sort field (stars, forks, updated) or None

    Returns:
        Dict with 'items' list containing repository data

    Raises:
        ValueError: If limit is not positive or sort is not a known value.
        GhError: If the gh CLI fails, is not installed, or is not authenticated.
    """
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")
    if sort is not None and sort not in _VALID_SORTS:
        raise ValueError(f"invalid sort '{sort}'; expected one of {sorted(_VALID_SORTS)}")

    base_cmd = ["gh", "search", "repos"]
    for name, value in spec.qualifiers:
        flag = QUALIFIER_FLAGS.get(name, f"--{name}")
        base_cmd.extend([flag, value])

    keywords = spec.keywords
    # Multi-keyword strategy: search each keyword separately and merge.
    # gh search repos treats multiple words as AND, which returns nothing
    # for diverse keyword sets. Per-keyword OR semantics give much better
    # coverage. Phrases stay intact as single argv elements either way.
    if len(keywords) > 1:
        # Over-fetch per keyword (floor of even split, min 5) because dedup
        # shrinks the merged pool; the merged result is sliced to `limit`.
        per_kw_limit = max(limit // len(keywords), 5)
        return _multi_keyword_search(base_cmd, keywords, per_kw_limit, limit, sort)

    cmd = list(base_cmd)
    if keywords:
        cmd.append(keywords[0])
    if sort:
        cmd.extend(["--sort", sort, "--order", "desc"])
    cmd.extend(["--limit", str(limit), "--json", _JSON_FIELDS])

    return {"items": _run_repo_search(cmd)}


def get_repo(owner: str, repo: str) -> dict[str, Any]:
    """Get detailed information about a repository.

    Args:
        owner: Repository owner username
        repo: Repository name

    Returns:
        Parsed JSON response from GitHub API

    Raises:
        ValueError: If owner or repo contains characters outside [A-Za-z0-9._-].
        GhError: If the gh CLI fails, is not installed, or is not authenticated.
    """
    if not _NAME_PATTERN.match(owner):
        raise ValueError(f"invalid repository owner '{owner}'")
    if not _NAME_PATTERN.match(repo):
        raise ValueError(f"invalid repository name '{repo}'")

    result = _run_gh(["gh", "api", f"repos/{owner}/{repo}"])
    if result.returncode != 0:
        _raise_for_gh_error(result.stderr.strip(), result.returncode, not_found=f"{owner}/{repo}")

    try:
        data: dict[str, Any] = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise GhError(f"Invalid JSON response from GitHub API: {e}") from e
    return data
