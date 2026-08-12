"""Pure query construction — no I/O, no subprocess."""

from __future__ import annotations

from grave.models.search import SearchSpec


def build_search_query(
    keywords: list[str] | None = None,
    created_range: str | None = None,
    language: str | None = None,
    stars_range: str | None = None,
    pushed: str | None = None,
) -> SearchSpec:
    """Build a SearchSpec, keeping keywords separate from GitHub search qualifiers."""
    qualifiers: list[tuple[str, str]] = []
    if created_range:
        qualifiers.append(("created", created_range))
    if language:
        qualifiers.append(("language", language))
    if stars_range:
        qualifiers.append(("stars", stars_range))
    if pushed:
        qualifiers.append(("pushed", pushed))

    return SearchSpec(keywords=list(keywords or []), qualifiers=qualifiers)
