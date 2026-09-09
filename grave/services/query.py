"""Pure query construction — no I/O, no subprocess."""

from __future__ import annotations

from typing import TYPE_CHECKING

from grave.models.search import SearchFilters, SearchSpec

if TYPE_CHECKING:
    from grave.models.preset import Preset


def build_search_query(
    keywords: list[str] | None = None, filters: SearchFilters | None = None
) -> SearchSpec:
    """Build a SearchSpec, keeping keywords separate from GitHub search qualifiers."""
    f = filters or SearchFilters()
    qualifiers: list[tuple[str, str]] = []
    if f.created_range:
        qualifiers.append(("created", f.created_range))
    if f.language:
        qualifiers.append(("language", f.language))
    if f.stars_range:
        qualifiers.append(("stars", f.stars_range))
    if f.pushed:
        qualifiers.append(("pushed", f.pushed))
    if f.archived is not None:
        qualifiers.append(("archived", "true" if f.archived else "false"))
    if f.match:
        qualifiers.append(("match", f.match))
    if f.size:
        qualifiers.append(("size", f.size))
    if f.include_forks:
        qualifiers.append(("include-forks", f.include_forks))

    return SearchSpec(keywords=list(keywords or []), qualifiers=qualifiers)


def build_preset_query(
    preset: Preset,
    *,
    language: str | None = None,
    stars_range: str | None = None,
) -> SearchSpec:
    """Turn a preset into a SearchSpec; explicit language/stars override the preset's own."""
    filters = SearchFilters(
        created_range=preset.created_range,
        language=language or preset.language,
        stars_range=stars_range or preset.stars_range,
        pushed=preset.pushed,
        archived=preset.archived,
        match=preset.match,
        size=preset.size,
        include_forks=preset.include_forks,
    )
    return build_search_query(keywords=preset.keywords or None, filters=filters)
