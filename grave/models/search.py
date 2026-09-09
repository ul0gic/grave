"""Imports only stdlib — models must never form import cycles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple


@dataclass(frozen=True)
class SearchFilters:
    """Every GitHub qualifier grave knows how to pass; None means "not filtered"."""

    created_range: str | None = None
    language: str | None = None
    stars_range: str | None = None
    pushed: str | None = None
    archived: bool | None = None
    match: str | None = None
    size: str | None = None
    include_forks: str | None = None


class SearchSpec(NamedTuple):
    """Keywords are never flattened into one string — multi-word phrases must
    survive as single argv elements to gh."""

    keywords: list[str]
    qualifiers: list[tuple[str, str]]

    def display(self) -> str:
        """Human-readable query string for logging and display."""
        parts = [*self.keywords, *(f"{name}:{value}" for name, value in self.qualifiers)]
        return " ".join(parts)
