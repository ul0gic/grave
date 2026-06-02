"""The ``grave presets`` command: list available preset search profiles."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def cmd_presets(args: argparse.Namespace) -> None:
    """List all available preset search profiles."""
    from grave.config.presets import list_categories, list_presets
    from grave.view.display import display_presets

    try:
        # Validate category if provided
        if args.category:
            available_categories = list_categories()
            if args.category not in available_categories:
                print(
                    f"grave: error: invalid category '{args.category}'",
                    file=sys.stderr,
                )
                print(
                    f"Available categories: {', '.join(available_categories)}",
                    file=sys.stderr,
                )
                sys.exit(2)

        # Get presets (filtered by category if provided)
        presets = list_presets(category=args.category)
        display_presets(presets, category=args.category)
    except Exception as e:
        print(f"grave: error: failed to list presets: {e}", file=sys.stderr)
        sys.exit(1)
