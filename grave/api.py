"""GitHub API client using gh CLI subprocess calls.

This module provides functions for interacting with the GitHub API
using the gh CLI tool via subprocess calls. It handles search queries
and repository detail fetching.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def _is_first_run() -> bool:
    """Check if this is a first-run scenario.

    Returns:
        True if the data directory does not exist, False otherwise
    """
    data_home = os.environ.get("XDG_DATA_HOME")
    if data_home:
        data_dir = Path(data_home) / "grave"
    else:
        data_dir = Path.home() / ".local" / "share" / "grave"

    return not data_dir.exists()


def check_gh_auth() -> bool:
    """Check if gh CLI is installed and authenticated.

    Returns:
        True if gh is authenticated, False otherwise

    Prints error messages to stderr with helpful guidance.
    """
    try:
        # Check if gh is installed and authenticated
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            # Check if this is a first-run scenario
            if _is_first_run():
                print(
                    "⚰️  Looks like this is your first time running GRAVE.",
                    file=sys.stderr,
                )
                print("Run 'grave init' to get set up.", file=sys.stderr)
                return False

            stderr = result.stderr.strip()

            # Check for common error patterns
            if "not logged" in stderr.lower() or "not authenticated" in stderr.lower():
                print(
                    "grave: error: GitHub authentication required",
                    file=sys.stderr,
                )
                print("Run: gh auth login", file=sys.stderr)
                return False

            # Generic auth check failure
            print(
                "grave: error: unable to verify GitHub authentication",
                file=sys.stderr,
            )
            print("Run: gh auth login", file=sys.stderr)
            return False

        return True

    except FileNotFoundError:
        # Check if this is a first-run scenario
        if _is_first_run():
            print(
                "⚰️  Looks like this is your first time running GRAVE.",
                file=sys.stderr,
            )
            print("Run 'grave init' to get set up.", file=sys.stderr)
            return False

        print(
            "grave: error: gh CLI not found",
            file=sys.stderr,
        )
        print("Install it: https://cli.github.com", file=sys.stderr)
        return False


def build_search_query(
    keywords: list[str] | None = None,
    created_range: str | None = None,
    language: str | None = None,
    stars_range: str | None = None,
    pushed: str | None = None,
) -> str:
    """Build a GitHub search query string from parameters.

    Args:
        keywords: List of keywords to search for
        created_range: Date range for repository creation
            (e.g., '2008-01-01..2010-12-31')
        language: Programming language filter
        stars_range: Star count filter (e.g., '>100', '10..50', '>=1')
        pushed: Last push date filter (e.g., '<2015-01-01')

    Returns:
        Valid GitHub search query string

    Example:
        >>> build_search_query(
        ...     keywords=["democracy", "utopia"],
        ...     created_range="2008-01-01..2012-12-31",
        ...     language="Python",
        ...     stars_range=">10"
        ... )
        'democracy utopia created:2008-01-01..2012-12-31 language:Python stars:>10'
    """
    parts = []

    # Add keywords first
    if keywords:
        parts.extend(keywords)

    # Add qualifiers
    if created_range:
        parts.append(f"created:{created_range}")

    if language:
        parts.append(f"language:{language}")

    if stars_range:
        parts.append(f"stars:{stars_range}")

    if pushed:
        parts.append(f"pushed:{pushed}")

    return " ".join(parts)


_JSON_FIELDS = (
    "fullName,description,stargazersCount,forksCount,watchersCount,"
    "openIssuesCount,language,createdAt,pushedAt,updatedAt,url"
)


def _normalize_item(item: dict) -> dict:
    """Convert gh CLI JSON field names to snake_case GitHub API format."""
    return {
        "full_name": item.get("fullName", ""),
        "description": item.get("description", ""),
        "stargazers_count": item.get("stargazersCount", 0),
        "forks_count": item.get("forksCount", 0),
        "watchers_count": item.get("watchersCount", 0),
        "open_issues_count": item.get("openIssuesCount", 0),
        "language": item.get("language", ""),
        "created_at": item.get("createdAt", ""),
        "pushed_at": item.get("pushedAt", ""),
        "updated_at": item.get("updatedAt", ""),
        "topics": [],
        "html_url": item.get("url", ""),
    }


def _multi_keyword_search(
    base_cmd: list[str],
    keywords: list[str],
    per_kw_limit: int,
    total_limit: int,
    sort: str | None,
) -> dict:
    """Search each keyword separately and merge results, deduped by full_name."""
    seen = set()
    merged = []

    for keyword in keywords:
        cmd = [*base_cmd, keyword]
        if sort:
            cmd.extend(["--sort", sort, "--order", "desc"])
        cmd.extend(["--limit", str(per_kw_limit), "--json", _JSON_FIELDS])

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            continue

        try:
            items = json.loads(result.stdout)
        except json.JSONDecodeError:
            continue

        for item in items:
            name = item.get("fullName", "")
            if name not in seen:
                seen.add(name)
                merged.append(_normalize_item(item))

    # Sort merged results by stars descending and cap at total_limit
    merged.sort(key=lambda r: r["stargazers_count"], reverse=True)
    return {"items": merged[:total_limit]}


def search_repos(query: str, limit: int = 30, sort: str | None = None) -> dict:
    """Search GitHub repositories using gh CLI.

    Args:
        query: GitHub search query string
        limit: Maximum number of results to return
        sort: Sort field (stars, forks, updated, etc.)

    Returns:
        Dict with 'items' list containing repository data

    Raises:
        RuntimeError: If gh CLI fails or is not authenticated
    """
    try:
        # Parse query string to extract gh search repos parameters
        # Format: "keyword1 keyword2 created:range language:lang stars:range"
        base_cmd = ["gh", "search", "repos"]

        # Separate keywords from qualifiers
        parts = query.split()
        keywords = []
        for part in parts:
            if ":" in part:
                qualifier, value = part.split(":", 1)
                if qualifier == "created":
                    base_cmd.extend(["--created", value])
                elif qualifier == "language":
                    base_cmd.extend(["--language", value])
                elif qualifier == "stars":
                    base_cmd.extend(["--stars", value])
                elif qualifier == "pushed":
                    base_cmd.extend(["--updated", value])
            else:
                keywords.append(part)

        # Multi-keyword strategy: search each keyword separately and merge.
        # gh search repos treats multiple words as AND which returns nothing
        # for diverse keyword sets. Searching per-keyword with OR semantics
        # gives much better coverage.
        if len(keywords) > 1:
            per_kw_limit = max(limit // len(keywords), 5)
            return _multi_keyword_search(
                base_cmd, keywords, per_kw_limit, limit, sort,
            )

        # Single keyword or no keywords
        cmd = list(base_cmd)
        if keywords:
            cmd.append(keywords[0])

        # Add sort parameter
        if sort:
            cmd.extend(["--sort", sort, "--order", "desc"])

        # Add limit
        cmd.extend(["--limit", str(limit)])

        # Request JSON output with required fields
        cmd.extend(["--json", _JSON_FIELDS])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        # Handle gh CLI errors
        if result.returncode != 0:
            stderr = result.stderr.strip()

            # Check for common error patterns
            if "gh: command not found" in stderr or "not found" in stderr:
                print(
                    "gh CLI not found. Install it: https://cli.github.com",
                    file=sys.stderr,
                )
                raise RuntimeError("gh CLI not installed")

            if "authentication" in stderr.lower() or "401" in stderr:
                print(
                    "GitHub API error: not authenticated. Run: gh auth login",
                    file=sys.stderr,
                )
                raise RuntimeError("GitHub authentication required")

            if "rate limit" in stderr.lower() or "403" in stderr:
                print(
                    "GitHub API error: rate limit exceeded. Try again later.",
                    file=sys.stderr,
                )
                raise RuntimeError("GitHub API rate limit exceeded")

            # Generic error
            print(f"GitHub API error: {stderr}", file=sys.stderr)
            raise RuntimeError(f"gh CLI failed with exit code {result.returncode}")

        # Parse JSON response - gh search repos returns array directly
        try:
            items = json.loads(result.stdout)
            return {"items": [_normalize_item(item) for item in items]}
        except json.JSONDecodeError as e:
            print(f"Failed to parse GitHub API response: {e}", file=sys.stderr)
            raise RuntimeError("Invalid JSON response from GitHub API") from e

    except FileNotFoundError as e:
        print(
            "gh CLI not found. Install it: https://cli.github.com",
            file=sys.stderr,
        )
        raise RuntimeError("gh CLI not installed") from e


def get_repo(owner: str, repo: str) -> dict:
    """Get detailed information about a repository.

    Args:
        owner: Repository owner username
        repo: Repository name

    Returns:
        Parsed JSON response from GitHub API

    Raises:
        RuntimeError: If gh CLI fails or is not authenticated
    """
    try:
        # Build gh API command
        result = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Handle gh CLI errors
        if result.returncode != 0:
            stderr = result.stderr.strip()

            # Check for common error patterns
            if "gh: command not found" in stderr or "not found" in stderr:
                print(
                    "gh CLI not found. Install it: https://cli.github.com",
                    file=sys.stderr,
                )
                raise RuntimeError("gh CLI not installed")

            if "authentication" in stderr.lower() or "401" in stderr:
                print(
                    "GitHub API error: not authenticated. Run: gh auth login",
                    file=sys.stderr,
                )
                raise RuntimeError("GitHub authentication required")

            if "404" in stderr or "not found" in stderr.lower():
                print(f"Repository not found: {owner}/{repo}", file=sys.stderr)
                raise RuntimeError(f"Repository not found: {owner}/{repo}")

            if "rate limit" in stderr.lower() or "403" in stderr:
                print(
                    "GitHub API error: rate limit exceeded. Try again later.",
                    file=sys.stderr,
                )
                raise RuntimeError("GitHub API rate limit exceeded")

            # Generic error
            print(f"GitHub API error: {stderr}", file=sys.stderr)
            raise RuntimeError(f"gh CLI failed with exit code {result.returncode}")

        # Parse JSON response
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print(f"Failed to parse GitHub API response: {e}", file=sys.stderr)
            raise RuntimeError("Invalid JSON response from GitHub API") from e

    except FileNotFoundError as e:
        print(
            "gh CLI not found. Install it: https://cli.github.com",
            file=sys.stderr,
        )
        raise RuntimeError("gh CLI not installed") from e
