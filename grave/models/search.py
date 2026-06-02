"""Structured GitHub repository search specification.

Defines the immutable :class:`SearchSpec` produced by ``api.build_search_query``
and consumed by ``api.search_repos``. Pure data plus a formatting helper; imports
nothing first-party so it never participates in an import cycle.
"""

from __future__ import annotations

from typing import NamedTuple


class SearchSpec(NamedTuple):
    """A structured GitHub repository search, keeping keywords distinct from qualifiers.

    Multi-word keyword phrases (e.g. "neural network") must survive as single
    argv elements to ``gh search repos``, so keywords are never flattened into a
    space-joined string.
    """

    keywords: list[str]
    qualifiers: list[tuple[str, str]]

    def display(self) -> str:
        """Human-readable query string for logging and database storage."""
        parts = [*self.keywords, *(f"{name}:{value}" for name, value in self.qualifiers)]
        return " ".join(parts)
