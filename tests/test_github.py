"""Unit and integration tests for grave.integrations.github.

The gh CLI is the only true boundary here, so ``subprocess.run`` is the only
thing mocked. Pure functions (_normalize_item) run with no mocking at all;
build_search_query now lives in grave.services and is tested there.
"""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest

from grave.integrations import github
from grave.integrations.github import (
    GhAuthError,
    GhError,
    GhNotFoundError,
    GhNotInstalledError,
    GhRateLimitError,
    GhTimeoutError,
)
from grave.models.search import SearchSpec

if TYPE_CHECKING:
    from collections.abc import Sequence


# --------------------------------------------------------------------------- #
# _normalize_item — None semantics and defaults
# --------------------------------------------------------------------------- #


def test_normalize_item_maps_camelcase_to_snake_case() -> None:
    raw = {"fullName": "owner/repo", "stargazersCount": 42, "url": "https://x"}
    result = github._normalize_item(raw)
    assert result["full_name"] == "owner/repo"
    assert result["stargazers_count"] == 42
    assert result["html_url"] == "https://x"


def test_normalize_item_missing_description_is_none() -> None:
    result = github._normalize_item({"fullName": "a/b"})
    assert result["description"] is None


def test_normalize_item_missing_language_is_none() -> None:
    result = github._normalize_item({"fullName": "a/b"})
    assert result["language"] is None


def test_normalize_item_empty_string_description_becomes_none() -> None:
    # `or None` collapses "" to None so blank rows never surface downstream.
    result = github._normalize_item({"fullName": "a/b", "description": ""})
    assert result["description"] is None


def test_normalize_item_empty_string_language_becomes_none() -> None:
    result = github._normalize_item({"fullName": "a/b", "language": ""})
    assert result["language"] is None


def test_normalize_item_count_defaults_are_zero() -> None:
    result = github._normalize_item({"fullName": "a/b"})
    assert result["stargazers_count"] == 0
    assert result["forks_count"] == 0
    assert result["watchers_count"] == 0
    assert result["open_issues_count"] == 0


def test_normalize_item_always_has_all_keys() -> None:
    result = github._normalize_item({})
    expected = {
        "full_name",
        "description",
        "stargazers_count",
        "forks_count",
        "watchers_count",
        "open_issues_count",
        "language",
        "created_at",
        "pushed_at",
        "updated_at",
        "topics",
        "html_url",
    }
    assert set(result.keys()) == expected


def test_normalize_item_topics_always_empty_list() -> None:
    # Search results carry no topics; they are always [] regardless of input.
    result = github._normalize_item({"fullName": "a/b", "topics": ["x", "y"]})
    assert result["topics"] == []


def test_normalize_item_preserves_zero_stars_not_default() -> None:
    result = github._normalize_item({"fullName": "a/b", "stargazersCount": 0})
    assert result["stargazers_count"] == 0


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #


def _gh_result(stdout: str = "[]", returncode: int = 0, stderr: str = "") -> MagicMock:
    """Build a fake CompletedProcess-like object for subprocess.run."""
    mock = MagicMock()
    mock.returncode = returncode
    mock.stdout = stdout
    mock.stderr = stderr
    return mock


# --------------------------------------------------------------------------- #
# _run_gh — the single subprocess funnel: timeout retry, transient retry
# --------------------------------------------------------------------------- #


def test_run_gh_returns_completed_process_on_success() -> None:
    with patch.object(subprocess, "run", return_value=_gh_result("[]")) as run:
        result = github._run_gh(["gh", "auth", "status"])
    assert result.returncode == 0
    run.assert_called_once()
    # The timeout is always passed to the boundary.
    assert run.call_args.kwargs["timeout"] == 30
    assert run.call_args.kwargs["capture_output"] is True
    assert run.call_args.kwargs["text"] is True
    assert run.call_args.kwargs["check"] is False


def test_run_gh_missing_executable_raises_not_installed_without_retry() -> None:
    with (
        patch.object(subprocess, "run", side_effect=FileNotFoundError) as run,
        pytest.raises(GhNotInstalledError, match="not found"),
    ):
        github._run_gh(["gh", "auth", "status"])
    # FileNotFoundError is unrecoverable — no retry.
    run.assert_called_once()


def test_run_gh_retries_once_then_raises_timeout() -> None:
    timeout_err = subprocess.TimeoutExpired(cmd=["gh"], timeout=30)
    with (
        patch.object(subprocess, "run", side_effect=timeout_err) as run,
        pytest.raises(GhTimeoutError, match="timed out"),
    ):
        github._run_gh(["gh", "search", "repos"])
    # One initial attempt + exactly one retry.
    assert run.call_count == 2


def test_run_gh_retry_succeeds_after_first_timeout() -> None:
    timeout_err = subprocess.TimeoutExpired(cmd=["gh"], timeout=30)
    with patch.object(subprocess, "run", side_effect=[timeout_err, _gh_result("[]")]) as run:
        result = github._run_gh(["gh", "search", "repos"])
    assert result.returncode == 0
    assert run.call_count == 2


def test_run_gh_retries_once_then_raises_on_transient_oserror() -> None:
    with (
        patch.object(subprocess, "run", side_effect=OSError("connection reset")) as run,
        pytest.raises(GhError, match="failed to run"),
    ):
        github._run_gh(["gh", "search", "repos"])
    assert run.call_count == 2


def test_run_gh_transient_oserror_then_timeout_raises_timeout() -> None:
    timeout_err = subprocess.TimeoutExpired(cmd=["gh"], timeout=30)
    with (
        patch.object(subprocess, "run", side_effect=[OSError("reset"), timeout_err]) as run,
        pytest.raises(GhTimeoutError, match="timed out"),
    ):
        github._run_gh(["gh", "search", "repos"])
    assert run.call_count == 2


# --------------------------------------------------------------------------- #
# search_repos — mock only the subprocess boundary
# --------------------------------------------------------------------------- #


def test_search_repos_single_keyword_builds_expected_cmd() -> None:
    spec = SearchSpec(keywords=["fractal"], qualifiers=[("language", "C")])
    with patch.object(subprocess, "run", return_value=_gh_result("[]")) as run:
        github.search_repos(spec, limit=7, sort="stars")
    cmd = run.call_args.args[0]
    assert cmd[:3] == ["gh", "search", "repos"]
    assert "--language" in cmd
    assert "fractal" in cmd
    assert "--limit" in cmd and "7" in cmd
    assert "--sort" in cmd and "stars" in cmd


def test_search_repos_pushed_qualifier_maps_to_updated_flag() -> None:
    spec = SearchSpec(keywords=[], qualifiers=[("pushed", "<2015-01-01")])
    with patch.object(subprocess, "run", return_value=_gh_result("[]")) as run:
        github.search_repos(spec)
    cmd = run.call_args.args[0]
    assert "--updated" in cmd
    assert "--pushed" not in cmd
    assert cmd[cmd.index("--updated") + 1] == "<2015-01-01"


def test_search_repos_no_sort_omits_sort_flags() -> None:
    spec = SearchSpec(keywords=["x"], qualifiers=[])
    with patch.object(subprocess, "run", return_value=_gh_result("[]")) as run:
        github.search_repos(spec, sort=None)
    cmd = run.call_args.args[0]
    assert "--sort" not in cmd


def test_search_repos_normalizes_returned_items() -> None:
    payload = json.dumps([{"fullName": "a/b", "stargazersCount": 5}])
    spec = SearchSpec(keywords=["x"], qualifiers=[])
    with patch.object(subprocess, "run", return_value=_gh_result(payload)):
        result = github.search_repos(spec)
    assert result["items"][0]["full_name"] == "a/b"
    assert result["items"][0]["stargazers_count"] == 5
    assert result["items"][0]["language"] is None


def test_search_repos_empty_keywords_omits_query_term() -> None:
    spec = SearchSpec(keywords=[], qualifiers=[("language", "Go")])
    with patch.object(subprocess, "run", return_value=_gh_result("[]")) as run:
        github.search_repos(spec)
    cmd = run.call_args.args[0]
    # Only flag/value pairs and the literal subcommand — no bare keyword.
    assert cmd == [
        "gh",
        "search",
        "repos",
        "--language",
        "Go",
        "--limit",
        "30",
        "--json",
        github._JSON_FIELDS,
    ]


def test_search_repos_rejects_nonpositive_limit() -> None:
    spec = SearchSpec(keywords=["x"], qualifiers=[])
    with (
        patch.object(subprocess, "run") as run,
        pytest.raises(ValueError, match="limit must be positive"),
    ):
        github.search_repos(spec, limit=0)
    # Validation happens before any subprocess call.
    run.assert_not_called()


def test_search_repos_rejects_unknown_sort() -> None:
    spec = SearchSpec(keywords=["x"], qualifiers=[])
    with (
        patch.object(subprocess, "run") as run,
        pytest.raises(ValueError, match="invalid sort"),
    ):
        github.search_repos(spec, sort="downloads")
    run.assert_not_called()


def test_search_repos_auth_failure_raises_auth_error() -> None:
    spec = SearchSpec(keywords=["x"], qualifiers=[])
    failed = _gh_result(returncode=1, stderr="HTTP 401: authentication failed")
    with (
        patch.object(subprocess, "run", return_value=failed),
        pytest.raises(GhAuthError),
    ):
        github.search_repos(spec)


def test_search_repos_rate_limit_raises_and_is_not_retried() -> None:
    spec = SearchSpec(keywords=["x"], qualifiers=[])
    failed = _gh_result(returncode=1, stderr="HTTP 403: API rate limit exceeded")
    with (
        patch.object(subprocess, "run", return_value=failed) as run,
        pytest.raises(GhRateLimitError),
    ):
        github.search_repos(spec)
    # Rate-limit is a returncode failure, never retried: exactly one call.
    run.assert_called_once()


def test_search_repos_gh_missing_raises_not_installed() -> None:
    spec = SearchSpec(keywords=["x"], qualifiers=[])
    with (
        patch.object(subprocess, "run", side_effect=FileNotFoundError),
        pytest.raises(GhNotInstalledError, match="not found"),
    ):
        github.search_repos(spec)


def test_search_repos_bad_json_raises_gh_error() -> None:
    spec = SearchSpec(keywords=["x"], qualifiers=[])
    with (
        patch.object(subprocess, "run", return_value=_gh_result("not json")),
        pytest.raises(GhError, match="Invalid JSON"),
    ):
        github.search_repos(spec)


def test_search_repos_generic_failure_raises_gh_error() -> None:
    spec = SearchSpec(keywords=["x"], qualifiers=[])
    failed = _gh_result(returncode=2, stderr="something exploded")
    with (
        patch.object(subprocess, "run", return_value=failed),
        pytest.raises(GhError, match="exit code 2"),
    ):
        github.search_repos(spec)


# --------------------------------------------------------------------------- #
# _multi_keyword_search — OR-merge, dedup by full_name, client-side sort
# --------------------------------------------------------------------------- #


def _multi_run_factory(
    responses: dict[str, Sequence[dict[str, Any]]],
) -> Any:
    """Return a subprocess.run stand-in that keys its payload off the keyword.

    The keyword is the final positional argv element appended by
    _multi_keyword_search, so we read it from the command tail.
    """

    def fake_run(cmd: list[str], **_kwargs: Any) -> MagicMock:
        # The keyword sits just before "--sort"/"--limit" flags; find the last
        # element that is not a flag value by scanning known structure.
        # base_cmd ... <keyword> [--sort s --order desc] --limit N --json FIELDS
        keyword = cmd[cmd.index("--limit") - 1]
        if keyword == "desc":  # came from --order desc, keyword precedes --sort
            keyword = cmd[cmd.index("--sort") - 1]
        payload = json.dumps(list(responses.get(keyword, [])))
        return _gh_result(payload)

    return fake_run


def test_multi_keyword_search_dedupes_by_full_name() -> None:
    spec = SearchSpec(keywords=["alpha", "beta"], qualifiers=[])
    responses = {
        "alpha": [{"fullName": "x/shared", "stargazersCount": 10}],
        "beta": [
            {"fullName": "x/shared", "stargazersCount": 10},
            {"fullName": "y/unique", "stargazersCount": 20},
        ],
    }
    with patch.object(subprocess, "run", side_effect=_multi_run_factory(responses)):
        result = github.search_repos(spec, limit=30, sort=None)
    names = [r["full_name"] for r in result["items"]]
    assert names.count("x/shared") == 1
    assert set(names) == {"x/shared", "y/unique"}


def test_multi_keyword_search_sorts_by_stars_desc() -> None:
    spec = SearchSpec(keywords=["alpha", "beta"], qualifiers=[])
    responses = {
        "alpha": [{"fullName": "a/low", "stargazersCount": 1}],
        "beta": [{"fullName": "b/high", "stargazersCount": 99}],
    }
    with patch.object(subprocess, "run", side_effect=_multi_run_factory(responses)):
        result = github.search_repos(spec, limit=30, sort="stars")
    assert [r["full_name"] for r in result["items"]] == ["b/high", "a/low"]


def test_multi_keyword_search_respects_total_limit() -> None:
    spec = SearchSpec(keywords=["alpha", "beta"], qualifiers=[])
    responses = {
        "alpha": [{"fullName": f"a/{i}", "stargazersCount": i + 1} for i in range(10)],
        "beta": [{"fullName": f"b/{i}", "stargazersCount": i + 1} for i in range(10)],
    }
    with patch.object(subprocess, "run", side_effect=_multi_run_factory(responses)):
        result = github.search_repos(spec, limit=5, sort="stars")
    assert len(result["items"]) == 5


def test_multi_keyword_search_handles_zero_stars_mixed_with_nonzero() -> None:
    # Regression: _merge_sort_key must not coerce a legitimate 0 to "" (a str/int
    # mix would raise TypeError when a multi-keyword merge contains both 0 and >0).
    spec = SearchSpec(keywords=["alpha", "beta"], qualifiers=[])
    responses = {
        "alpha": [{"fullName": "a/zero", "stargazersCount": 0}],
        "beta": [{"fullName": "b/five", "stargazersCount": 5}],
    }
    with patch.object(subprocess, "run", side_effect=_multi_run_factory(responses)):
        result = github.search_repos(spec, limit=30, sort="stars")
    # Correct behavior would sort 5 above 0 without crashing.
    assert [r["full_name"] for r in result["items"]] == ["b/five", "a/zero"]


def test_multi_keyword_search_sort_updated_uses_updated_at() -> None:
    spec = SearchSpec(keywords=["alpha", "beta"], qualifiers=[])
    responses = {
        "alpha": [{"fullName": "a/old", "updatedAt": "2010-01-01T00:00:00Z"}],
        "beta": [{"fullName": "b/new", "updatedAt": "2020-01-01T00:00:00Z"}],
    }
    with patch.object(subprocess, "run", side_effect=_multi_run_factory(responses)):
        result = github.search_repos(spec, limit=30, sort="updated")
    assert [r["full_name"] for r in result["items"]] == ["b/new", "a/old"]


def test_multi_keyword_search_sort_forks_uses_forks_count() -> None:
    spec = SearchSpec(keywords=["alpha", "beta"], qualifiers=[])
    responses = {
        "alpha": [{"fullName": "a/few", "forksCount": 1}],
        "beta": [{"fullName": "b/many", "forksCount": 50}],
    }
    with patch.object(subprocess, "run", side_effect=_multi_run_factory(responses)):
        result = github.search_repos(spec, limit=30, sort="forks")
    assert [r["full_name"] for r in result["items"]] == ["b/many", "a/few"]


def test_search_repos_command_not_found_in_stderr_raises_not_installed() -> None:
    # gh present on PATH but its own stderr says "command not found" (e.g. a
    # broken shim): the returncode path must still classify it as not-installed.
    spec = SearchSpec(keywords=["x"], qualifiers=[])
    failed = _gh_result(returncode=127, stderr="gh: command not found")
    with (
        patch.object(subprocess, "run", return_value=failed),
        pytest.raises(GhNotInstalledError, match="not found"),
    ):
        github.search_repos(spec)


# --------------------------------------------------------------------------- #
# get_repo — boundary behavior and input validation
# --------------------------------------------------------------------------- #


def test_get_repo_returns_parsed_json() -> None:
    payload = json.dumps({"full_name": "owner/repo", "stargazers_count": 3})
    with patch.object(subprocess, "run", return_value=_gh_result(payload)):
        data = github.get_repo("owner", "repo")
    assert data["full_name"] == "owner/repo"


def test_get_repo_builds_correct_endpoint() -> None:
    with patch.object(subprocess, "run", return_value=_gh_result("{}")) as run:
        github.get_repo("torvalds", "linux")
    cmd = run.call_args.args[0]
    assert cmd == ["gh", "api", "repos/torvalds/linux"]


def test_get_repo_not_found_raises_with_repo_name() -> None:
    failed = _gh_result(returncode=1, stderr="HTTP 404: Not Found")
    with (
        patch.object(subprocess, "run", return_value=failed),
        pytest.raises(GhNotFoundError, match="Repository not found: owner/repo"),
    ):
        github.get_repo("owner", "repo")


def test_get_repo_gh_missing_raises_not_installed() -> None:
    with (
        patch.object(subprocess, "run", side_effect=FileNotFoundError),
        pytest.raises(GhNotInstalledError, match="not found"),
    ):
        github.get_repo("owner", "repo")


def test_get_repo_bad_json_raises_gh_error() -> None:
    with (
        patch.object(subprocess, "run", return_value=_gh_result("<<<not json")),
        pytest.raises(GhError, match="Invalid JSON"),
    ):
        github.get_repo("owner", "repo")


def test_get_repo_rate_limit_not_retried() -> None:
    failed = _gh_result(returncode=1, stderr="HTTP 403: API rate limit exceeded")
    with (
        patch.object(subprocess, "run", return_value=failed) as run,
        pytest.raises(GhRateLimitError),
    ):
        github.get_repo("owner", "repo")
    run.assert_called_once()


@pytest.mark.parametrize(
    ("owner", "repo"),
    [
        ("ow ner", "repo"),
        ("owner", "re po"),
        ("../etc", "repo"),
        ("owner", "repo;rm"),
        ("owner/extra", "repo"),
        ("", "repo"),
        ("owner", ""),
    ],
)
def test_get_repo_rejects_bad_charset_before_subprocess(owner: str, repo: str) -> None:
    with (
        patch.object(subprocess, "run") as run,
        pytest.raises(ValueError, match="invalid repository"),
    ):
        github.get_repo(owner, repo)
    run.assert_not_called()


def test_get_repo_accepts_dotted_and_dashed_names() -> None:
    with patch.object(subprocess, "run", return_value=_gh_result("{}")) as run:
        github.get_repo("my-org", "my.repo_v2")
    assert run.call_args.args[0] == ["gh", "api", "repos/my-org/my.repo_v2"]


# --------------------------------------------------------------------------- #
# check_gh_auth — now raises instead of returning bool / printing
# --------------------------------------------------------------------------- #


def test_check_gh_auth_succeeds_silently_when_authenticated() -> None:
    with patch.object(subprocess, "run", return_value=_gh_result(returncode=0)):
        assert github.check_gh_auth() is None


def test_check_gh_auth_raises_auth_error_when_not_authenticated() -> None:
    failed = _gh_result(returncode=1, stderr="You are not logged into any GitHub hosts")
    with (
        patch.object(subprocess, "run", return_value=failed),
        pytest.raises(GhAuthError, match="gh auth login"),
    ):
        github.check_gh_auth()


def test_check_gh_auth_message_mentions_grave_init() -> None:
    failed = _gh_result(returncode=1, stderr="not logged in")
    with (
        patch.object(subprocess, "run", return_value=failed),
        pytest.raises(GhAuthError) as exc,
    ):
        github.check_gh_auth()
    assert "grave init" in str(exc.value)


def test_check_gh_auth_raises_not_installed_when_gh_missing() -> None:
    with (
        patch.object(subprocess, "run", side_effect=FileNotFoundError),
        pytest.raises(GhNotInstalledError, match="not found"),
    ):
        github.check_gh_auth()
