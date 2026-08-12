"""These helpers raise UsageError for the dispatch layer — they never print or exit."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from grave.config.eras import ERAS
from grave.config.presets import get_preset, list_presets
from grave.errors import UsageError
from grave.services.query import build_search_query

if TYPE_CHECKING:
    import argparse

    from grave.models.preset import Preset
    from grave.models.search import SearchSpec

# Custom-search parameters shared by `scan` and `export`.
_SEARCH_PARAMS = (
    "keyword",
    "created",
    "pushed",
    "language",
    "stars",
    "abandoned",
    "era",
    "dead_since",
)


def build_custom_spec(args: argparse.Namespace) -> SearchSpec:
    """Build a SearchSpec from custom search flags; at least one is required."""
    if not any(getattr(args, name) is not None for name in _SEARCH_PARAMS):
        raise UsageError("at least one search parameter is required (or use --preset)")

    created_filter = args.created
    if args.era:
        start_date, end_date = ERAS[args.era]
        created_filter = f"{start_date}..{end_date}"

    # Pushed-filter precedence: --dead-since > --abandoned > --pushed.
    pushed_filter = args.pushed
    if args.dead_since is not None:
        if not 1970 <= args.dead_since <= date.today().year + 1:
            raise UsageError(f"invalid --dead-since year '{args.dead_since}'")
        pushed_filter = f"<{args.dead_since}-01-01"
    elif args.abandoned is not None:
        pushed_filter = abandoned_to_pushed(args.abandoned)

    return build_search_query(
        keywords=args.keyword,
        created_range=created_filter,
        language=args.language,
        stars_range=args.stars,
        pushed=pushed_filter,
    )


def abandoned_to_pushed(years: int) -> str:
    """Translate an --abandoned years value into a pushed:<date qualifier."""
    if years < 0:
        raise UsageError(f"invalid --abandoned years '{years}'")
    cutoff_year = date.today().year - years
    return f"<{cutoff_year}-01-01"


def resolve_preset_spec(args: argparse.Namespace) -> tuple[Preset, SearchSpec]:
    """Resolve a preset by name and build its SearchSpec, applying CLI overrides."""
    preset = get_preset(args.preset)
    if preset is None:
        names = "\n".join(f"  - {p.name}" for p in list_presets())
        raise UsageError(f"preset '{args.preset}' not found", "\nAvailable presets:", names)

    spec = build_search_query(
        keywords=preset.keywords or None,
        created_range=preset.created_range,
        language=args.language or preset.language,
        stars_range=args.stars or preset.stars_range,
        pushed=preset.pushed,
    )
    return preset, spec


def split_owner_repo(repo: str) -> tuple[str, str]:
    """Split an 'owner/repo' argument, rejecting anything not exactly two parts."""
    parts = repo.split("/")
    if len(parts) != 2 or not all(parts):
        raise UsageError(
            f"invalid repository format '{repo}'",
            "Expected format: owner/repo (e.g., 'torvalds/linux')",
        )
    return parts[0], parts[1]
