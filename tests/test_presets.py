"""Tests for grave config presets and the Preset model — pure data and query building."""

from __future__ import annotations

import pytest

from grave.config.presets import (
    CATALOG_MODULES,
    PRESETS,
    get_preset,
    list_categories,
    list_presets,
)
from grave.models.preset import Preset
from grave.models.search import SearchSpec
from grave.services.query import build_preset_query as _spec_for

_NEW_CATEGORIES = {"ahead-of-time", "dead-platforms", "dead-services", "human"}


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


def test_every_catalog_module_contributes_one_category() -> None:
    for module in CATALOG_MODULES:
        assert module.PRESETS
        assert len({p.category for p in module.PRESETS}) == 1


def test_new_categories_are_listed() -> None:
    assert set(list_categories()) >= _NEW_CATEGORIES


@pytest.mark.parametrize("preset", PRESETS, ids=[p.name for p in PRESETS])
def test_every_preset_filters_for_abandonment(preset: Preset) -> None:
    assert preset.pushed is not None
    assert preset.pushed.startswith("<")


@pytest.mark.parametrize("preset", PRESETS, ids=[p.name for p in PRESETS])
def test_preset_match_values_are_gh_fields(preset: Preset) -> None:
    if preset.match is not None:
        assert set(preset.match.split(",")) <= {"name", "description", "readme"}


def test_preset_new_qualifiers_reach_the_spec() -> None:
    preset = Preset(
        name="x",
        description="x",
        keywords=[],
        archived=True,
        match="name",
        size="<10",
        include_forks="only",
        pushed="<2015-01-01",
    )
    qual = dict(_spec_for(preset).qualifiers)
    assert qual["archived"] == "true"
    assert qual["match"] == "name"
    assert qual["size"] == "<10"
    assert qual["include-forks"] == "only"


def test_preset_query_overrides_language_and_stars() -> None:
    preset = get_preset("dead-lang-perl")
    assert preset is not None
    qual = dict(_spec_for(preset, language="Ruby", stars_range=">5").qualifiers)
    assert qual["language"] == "Ruby"
    assert qual["stars"] == ">5"


def test_graveyard_uses_real_archived_flag() -> None:
    preset = get_preset("graveyard")
    assert preset is not None
    assert dict(_spec_for(preset).qualifiers)["archived"] == "true"


def test_uber_for_x_keeps_phrase_quotes() -> None:
    preset = get_preset("uber-for-x")
    assert preset is not None
    assert '"uber for"' in _spec_for(preset).keywords


def test_tiny_gems_filters_on_size() -> None:
    preset = get_preset("tiny-gems")
    assert preset is not None
    assert dict(_spec_for(preset).qualifiers)["size"] == "<10"


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


def test_google_code_refugees_keeps_export_phrase() -> None:
    preset = get_preset("google-code-refugees")
    assert preset is not None
    spec = _spec_for(preset)
    assert "exported from code.google.com" in spec.keywords


def test_preset_qualifiers_reflect_fields() -> None:
    preset = get_preset("ancient")
    assert preset is not None
    spec = _spec_for(preset)
    qual = dict(spec.qualifiers)
    assert qual["created"] == "2008-01-01..2010-12-31"
    assert qual["stars"] == ">=1"
