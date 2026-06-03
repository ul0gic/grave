"""Shared data shapes for GRAVE.

Defines the normalized repository item produced by the search path
(`integrations.github._normalize_item`) and consumed by the view layer. Lives
in its own module so both the integration layer and downstream consumers can
import it without forming an import cycle.
"""

from __future__ import annotations

from typing import TypedDict


class RepoItem(TypedDict):
    """A normalized GitHub repository, snake_case to match the REST API shape.

    Every key is always present: `integrations.github._normalize_item` builds the dict as a
    literal with all fields populated, so the type is total. `description` and
    `language` may be None when GitHub omits them; the rest carry their fallback
    (empty string / zero / empty list) rather than being absent.
    """

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
