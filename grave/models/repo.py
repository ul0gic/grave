"""Imports only stdlib — models must never form import cycles."""

from __future__ import annotations

from typing import TypedDict


class RepoItem(TypedDict):
    """Total: every key is always present. None marks a value GitHub omitted;
    the rest fall back to ""/0/[] rather than being absent."""

    full_name: str
    description: str | None
    stargazers_count: int
    forks_count: int
    watchers_count: int
    open_issues_count: int
    language: str | None
    created_at: str
    pushed_at: str
    updated_at: str
    topics: list[str]
    html_url: str
