"""JSON goes to stdout for piping; the Rich table is for humans."""

from __future__ import annotations

import csv
import json
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grave.models.repo import RepoItem

_CSV_FIELDS: tuple[str, ...] = (
    "full_name",
    "description",
    "language",
    "stargazers_count",
    "created_at",
    "pushed_at",
    "html_url",
)


def emit_results(items: list[RepoItem], as_json: bool) -> None:
    """Emit results as JSON to stdout or as a Rich table."""
    if as_json:
        print(json.dumps(items, indent=2))
        return
    from grave.view.display import display_results

    display_results(items)


def write_export(items: list[RepoItem], fmt: str) -> None:
    """Write items to stdout as json, ndjson, or csv."""
    if fmt == "json":
        print(json.dumps(items, indent=2))
    elif fmt == "ndjson":
        for item in items:
            print(json.dumps(item))
    elif fmt == "csv":
        if not items:
            return
        writer = csv.DictWriter(sys.stdout, fieldnames=_CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(items)
