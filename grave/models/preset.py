"""Imports only stdlib — models must never form import cycles."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Preset:
    """A curated search: pure fields only, query building happens in the service layer."""

    name: str
    description: str
    keywords: list[str]
    created_range: str | None = None
    language: str | None = None
    stars_range: str | None = None
    pushed: str | None = None
    category: str = "general"
    sort: str = "stars"
    archived: bool | None = None
    match: str | None = None
    size: str | None = None
    include_forks: str | None = None
