"""The ``grave random`` command: pick a random preset and surface results."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from grave.view.output import emit_results

if TYPE_CHECKING:
    import argparse


def cmd_random(args: argparse.Namespace) -> None:
    """Pick a random preset and discover something unexpected."""
    import random

    from grave.config.presets import list_categories, list_presets
    from grave.errors import UsageError
    from grave.integrations.github import check_gh_auth, search_repos
    from grave.services.query import build_preset_query

    category = getattr(args, "category", None)
    if category is not None and category not in list_categories():
        raise UsageError(
            f"invalid category '{category}'",
            f"Available categories: {', '.join(list_categories())}",
        )

    check_gh_auth()

    preset = random.choice(list_presets(category=category))
    spec = build_preset_query(preset)
    response = search_repos(spec, limit=args.limit, sort=preset.sort)
    items = response.get("items", [])

    if args.json:
        print(json.dumps(items, indent=2))
        return

    from rich.console import Console

    console = Console()
    console.print()
    console.print(
        f"Random dig with preset: [bold cyan]{preset.name}[/bold cyan]",
        style="bold",
    )
    console.print(f"[dim]{preset.description}[/dim]")
    console.print()
    emit_results(items, as_json=False)
