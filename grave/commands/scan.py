"""The ``grave scan`` command: preset or custom repository search."""

from __future__ import annotations

from typing import TYPE_CHECKING

from grave.commands.specs import build_custom_spec, resolve_preset_spec
from grave.view.output import emit_results

if TYPE_CHECKING:
    import argparse


def cmd_scan(args: argparse.Namespace) -> None:
    """Run a repository scan with preset or custom parameters."""
    from grave.integrations.github import check_gh_auth, search_repos

    check_gh_auth()

    if args.preset:
        preset, spec = resolve_preset_spec(args)
        response = search_repos(spec, limit=args.limit, sort=preset.sort)
    else:
        spec = build_custom_spec(args)
        response = search_repos(spec, limit=args.limit, sort=args.sort)

    items = response.get("items", [])
    emit_results(items, args.json)
