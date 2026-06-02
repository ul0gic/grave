"""The ``grave export`` command: shape live search results as json/csv/ndjson."""

from __future__ import annotations

from typing import TYPE_CHECKING

from grave.commands.specs import build_custom_spec, resolve_preset_spec
from grave.view.output import write_export

if TYPE_CHECKING:
    import argparse

    from grave.models.repo import RepoItem


def _export_from_api(args: argparse.Namespace) -> list[RepoItem]:
    """Run a live search for export, mirroring `scan`'s preset/custom branching."""
    from grave.integrations.github import check_gh_auth, search_repos

    check_gh_auth()

    if args.preset:
        preset, spec = resolve_preset_spec(args)
        return search_repos(spec, limit=args.limit, sort=preset.sort).get("items", [])

    spec = build_custom_spec(args)
    return search_repos(spec, limit=args.limit, sort=args.sort).get("items", [])


def cmd_export(args: argparse.Namespace) -> None:
    """Export scan results in specified format."""
    items = _export_from_api(args)
    write_export(items, args.format)
