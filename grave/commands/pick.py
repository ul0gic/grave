"""TTY-gated: piped output, --json runs, and tests must never block on the prompt."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grave.models.repo import RepoItem


def prompt_dig(items: list[RepoItem]) -> None:
    """Offer to dig into a displayed result by its 1-indexed table number."""
    if not items or not sys.stdin.isatty() or not sys.stdout.isatty():
        return

    from grave.commands.specs import split_owner_repo
    from grave.integrations.github import get_repo
    from grave.view.display import display_repo_detail

    while True:
        try:
            raw = input(f"Dig into a result [1-{len(items)}] (Enter to exit): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not raw:
            return
        if not raw.isdigit() or not 1 <= int(raw) <= len(items):
            print(f"Pick a number between 1 and {len(items)}.")
            continue
        full_name = items[int(raw) - 1].get("full_name", "")
        owner, repo = split_owner_repo(full_name)
        display_repo_detail(get_repo(owner, repo))
