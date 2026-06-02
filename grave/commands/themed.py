"""Generic handler for the themed-lens commands (``morgue``, ``casket``).

Both commands are the same search differing only in their data, which lives in
:data:`grave.config.lenses.THEMED_LENSES`. The parser sets ``args.lens`` to the lens
name via ``set_defaults``; this handler looks it up and renders it. A future
lens is one table entry plus a subparser pointing here.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from grave.config.lenses import THEMED_LENSES
from grave.services.query import build_search_query
from grave.view.output import emit_results

if TYPE_CHECKING:
    import argparse


def cmd_themed(args: argparse.Namespace) -> None:
    """Run a themed-lens search and render its banner above the results."""
    from grave.integrations.github import check_gh_auth, search_repos

    check_gh_auth()

    lens = THEMED_LENSES[args.lens]
    spec = build_search_query(
        keywords=lens.keywords,
        created_range=lens.created_range,
        language=getattr(args, "language", None),
        pushed=lens.pushed,
    )
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
