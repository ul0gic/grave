"""Imports only stdlib — models must never form import cycles."""

from __future__ import annotations

from typing import NamedTuple


class SearchSpec(NamedTuple):
    """Keywords are never flattened into one string — multi-word phrases must
    survive as single argv elements to gh."""

    keywords: list[str]
    qualifiers: list[tuple[str, str]]

    def display(self) -> str:
        """Human-readable query string for logging and display."""
        parts = [*self.keywords, *(f"{name}:{value}" for name, value in self.qualifiers)]
        return " ".join(parts)
