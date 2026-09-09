"""Pure data — query building lives in the service layer, never here."""

from __future__ import annotations

from typing import TYPE_CHECKING

from grave.config.catalog import (
    ahead_of_time,
    archaeology,
    culture,
    dead_languages,
    dead_platforms,
    dead_services,
    eras,
    human,
    science,
)

if TYPE_CHECKING:
    from grave.models.preset import Preset

CATALOG_MODULES = (
    archaeology,
    dead_languages,
    eras,
    culture,
    science,
    ahead_of_time,
    dead_platforms,
    dead_services,
    human,
)

PRESETS: list[Preset] = [preset for module in CATALOG_MODULES for preset in module.PRESETS]


def list_presets(category: str | None = None) -> list[Preset]:
    """List presets, optionally filtered by category."""
    if category is None:
        return PRESETS
    return [p for p in PRESETS if p.category == category]


def list_categories() -> list[str]:
    """Sorted unique category names."""
    categories = {preset.category for preset in PRESETS}
    return sorted(categories)


def get_preset(name: str) -> Preset | None:
    """Look up a preset by name; None when unknown."""
    for preset in PRESETS:
        if preset.name == name:
            return preset
    return None
