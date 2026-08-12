"""Importable by test modules — conftest.py is reserved for fixtures and hooks."""

from __future__ import annotations

from typing import Any


def make_item(full_name: str = "owner/repo", **overrides: Any) -> dict[str, Any]:
    """A full RepoItem-shaped dict mirroring _normalize_item output; override via kwargs."""
    item: dict[str, Any] = {
        "full_name": full_name,
        "description": "a test repository",
        "stargazers_count": 10,
        "forks_count": 2,
        "watchers_count": 3,
        "open_issues_count": 1,
        "language": "Python",
        "created_at": "2010-01-01T00:00:00Z",
        "pushed_at": "2015-01-01T00:00:00Z",
        "updated_at": "2015-06-01T00:00:00Z",
        "topics": [],
        "html_url": f"https://github.com/{full_name}",
    }
    item.update(overrides)
    return item
