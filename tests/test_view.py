"""Tests for grave.view.

Only ``_format_date`` is unit-testable for an exact value; the Rich rendering
functions are smoke-tested for "does not raise and emits something" since their
visual output is not a stable contract.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from grave.view.display import _format_date, display_repo_detail, display_results

if TYPE_CHECKING:
    from grave.models.repo import RepoItem

from helpers import make_item


@pytest.mark.parametrize(
    ("iso", "expected"),
    [
        ("2010-03-15T12:00:00Z", "2010-03-15"),
        ("2010-03-15T12:00:00+00:00", "2010-03-15"),
        ("2008-01-01", "2008-01-01"),
        ("2020-12-31T23:59:59Z", "2020-12-31"),
    ],
)
def test_format_date_valid(iso: str, expected: str) -> None:
    assert _format_date(iso) == expected


@pytest.mark.parametrize(
    "garbage",
    ["", "not a date", "2010-13-45", "yesterday", "T12:00:00"],
)
def test_format_date_garbage_returns_na(garbage: str) -> None:
    assert _format_date(garbage) == "N/A"


def test_display_results_empty_prints_guidance(capsys: pytest.CaptureFixture[str]) -> None:
    display_results([])
    out = capsys.readouterr().out
    assert "No repositories found" in out


def test_display_results_renders_repo_names(capsys: pytest.CaptureFixture[str]) -> None:
    items: list[RepoItem] = [make_item("torvalds/linux")]  # type: ignore[list-item]
    display_results(items)
    out = capsys.readouterr().out
    assert "torvalds/linux" in out
    assert "Found 1 repositories" in out


def test_display_results_handles_none_language_and_description(
    capsys: pytest.CaptureFixture[str],
) -> None:
    items: list[RepoItem] = [make_item("a/b", language=None, description=None)]  # type: ignore[list-item]
    display_results(items)  # must not raise
    out = capsys.readouterr().out
    assert "a/b" in out


def test_display_repo_detail_renders(capsys: pytest.CaptureFixture[str]) -> None:
    repo = {
        "full_name": "owner/repo",
        "description": "a thing",
        "stargazers_count": 5,
        "forks_count": 1,
        "watchers_count": 2,
        "open_issues_count": 0,
        "language": "Python",
        "created_at": "2010-01-01T00:00:00Z",
        "pushed_at": "2015-01-01T00:00:00Z",
        "updated_at": "2016-01-01T00:00:00Z",
        "topics": ["cli", "archaeology"],
        "html_url": "https://github.com/owner/repo",
    }
    display_repo_detail(repo)
    out = capsys.readouterr().out
    assert "owner/repo" in out


def test_display_repo_detail_handles_missing_fields(capsys: pytest.CaptureFixture[str]) -> None:
    # Minimal dict — every .get() must fall back without raising.
    display_repo_detail({"full_name": "a/b"})
    out = capsys.readouterr().out
    assert "a/b" in out
