"""The ``grave rabbit-hole`` command: find repos similar to a given one."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from grave.commands.specs import split_owner_repo
from grave.view.output import emit_results

if TYPE_CHECKING:
    import argparse


def cmd_rabbit_hole(args: argparse.Namespace) -> None:
    """Find repos similar to a given repository."""
    from grave.integrations.github import check_gh_auth, get_repo, search_repos
    from grave.services.query import build_search_query

    check_gh_auth()

    owner, repo = split_owner_repo(args.repo)
    repo_data = get_repo(owner, repo)

    language = repo_data.get("language")
    created_at = repo_data.get("created_at", "")
    topics = repo_data.get("topics", [])

    # created_at is ISO format: "2008-04-10T12:34:56Z"
    created_year = int(created_at.split("-")[0]) if created_at else None

    # Similar repos = same language, up to 3 shared topics, ±2 years.
    created_range = None
    if created_year:
        created_range = f"{created_year - 2}-01-01..{created_year + 2}-12-31"

    spec = build_search_query(
        keywords=topics[:3] or None,
        created_range=created_range,
        language=language,
    )
    response = search_repos(spec, limit=args.limit)
    items = response.get("items", [])

    if args.json:
        print(json.dumps(items, indent=2))
        return

    from rich.console import Console

    console = Console()
    console.print()
    console.print(
        f"Down the rabbit hole from [bold cyan]{args.repo}[/bold cyan]...",
        style="bold",
    )
    if language:
        console.print(f"[dim]Language: {language}[/dim]")
    if created_year:
        console.print(f"[dim]Created: {created_year} (±2 years)[/dim]")
    if topics:
        console.print(f"[dim]Topics: {', '.join(topics[:3])}[/dim]")
    console.print()
    emit_results(items, as_json=False)
