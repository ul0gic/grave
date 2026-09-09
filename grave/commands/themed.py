"""One handler for all themed lenses — the parser sets args.lens via set_defaults."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from grave.config.lenses import THEMED_LENSES
from grave.models.search import SearchFilters
from grave.services.query import build_search_query
from grave.view.output import emit_results

if TYPE_CHECKING:
    import argparse


def cmd_themed(args: argparse.Namespace) -> None:
    """Run a themed-lens search and render its banner above the results."""
    from grave.integrations.github import check_gh_auth, search_repos

    check_gh_auth()

    lens = THEMED_LENSES[args.lens]
    filters = SearchFilters(
        created_range=lens.created_range,
        language=getattr(args, "language", None),
        stars_range=lens.stars_range,
        pushed=lens.pushed,
        archived=lens.archived,
        include_forks=lens.include_forks,
    )
    spec = build_search_query(keywords=lens.keywords, filters=filters)
    response = search_repos(spec, limit=args.limit)
    items = response.get("items", [])

    if args.json:
        print(json.dumps(items, indent=2))
        return

    from rich.console import Console

    console = Console()
    console.print()
    console.print(lens.header, style=lens.header_style)
    console.print(lens.blurb)
    console.print()
    emit_results(items, as_json=False)
