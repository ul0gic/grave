"""Tests for grave config presets and the Preset model — pure data and query building."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from grave.config.presets import PRESETS, get_preset, list_categories, list_presets
from grave.models.search import SearchSpec
from grave.services.query import build_search_query

if TYPE_CHECKING:
    from grave.models.preset import Preset


def _spec_for(preset: Preset) -> SearchSpec:
    """Build a SearchSpec from a preset's fields.

    Mirrors the conversion the CLI performs in ``_resolve_preset_spec``; query
    building was moved out of the Preset model to break the presets→api cycle.
    """
    return build_search_query(
        keywords=preset.keywords or None,
        created_range=preset.created_range,
        language=preset.language,
        stars_range=preset.stars_range,
        pushed=preset.pushed,
    )


def test_get_preset_returns_known() -> None:
    preset = get_preset("ancient")
    assert preset is not None
    assert preset.name == "ancient"
    assert preset.category == "archaeology"


def test_get_preset_unknown_returns_none() -> None:
    assert get_preset("nonexistent-preset") is None


def test_list_presets_returns_all() -> None:
    assert len(list_presets()) == len(PRESETS)


def test_list_presets_by_category_filters() -> None:
    dead = list_presets(category="dead-languages")
    assert dead  # non-empty
    assert all(p.category == "dead-languages" for p in dead)


def test_list_presets_unknown_category_returns_empty() -> None:
    assert list_presets(category="no-such-category") == []


def test_list_categories_sorted_and_unique() -> None:
    cats = list_categories()
    assert cats == sorted(cats)
    assert len(cats) == len(set(cats))


def test_list_categories_matches_preset_categories() -> None:
    expected = {p.category for p in PRESETS}
    assert set(list_categories()) == expected


def test_every_preset_has_unique_name() -> None:
    names = [p.name for p in PRESETS]
    assert len(names) == len(set(names))


@pytest.mark.parametrize("preset", PRESETS, ids=[p.name for p in PRESETS])
def test_preset_build_query_returns_valid_spec(preset: Preset) -> None:
    spec = _spec_for(preset)
    assert isinstance(spec, SearchSpec)
    assert isinstance(spec.keywords, list)
    assert isinstance(spec.qualifiers, list)
    # display() must not raise and must round-trip the keywords back out.
    rendered = spec.display()
    for kw in spec.keywords:
        assert kw in rendered


@pytest.mark.parametrize("preset", PRESETS, ids=[p.name for p in PRESETS])
def test_preset_sort_is_a_known_value(preset: Preset) -> None:
    assert preset.sort in {"stars", "forks", "updated"}


def test_preset_keywords_with_phrases_stay_intact() -> None:
    # "digital-utopia" has the multi-word keyword "virtual world".
    preset = get_preset("digital-utopia")
    assert preset is not None
    spec = _spec_for(preset)
    assert "virtual world" in spec.keywords


def test_preset_qualifiers_reflect_fields() -> None:
    preset = get_preset("ancient")
    assert preset is not None
    spec = _spec_for(preset)
    qual = dict(spec.qualifiers)
    assert qual["created"] == "2008-01-01..2010-12-31"
    assert qual["stars"] == ">=1"
