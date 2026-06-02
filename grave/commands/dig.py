"""The ``grave dig`` command: detailed information about one repository."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from grave.commands.specs import split_owner_repo

if TYPE_CHECKING:
    import argparse


def cmd_dig(args: argparse.Namespace) -> None:
    """Dig up detailed information about a repository."""
    from grave.integrations.github import check_gh_auth, get_repo
    from grave.view.display import display_repo_detail

    check_gh_auth()

    owner, repo = split_owner_repo(args.repo)
    repo_data = get_repo(owner, repo)

    if args.json:
        print(json.dumps(repo_data, indent=2))
    else:
        display_repo_detail(repo_data)

    if args.open:
        import webbrowser

        url = repo_data.get("html_url")
        if url:
            print(f"Opening {url} in browser...")
            webbrowser.open(url)
