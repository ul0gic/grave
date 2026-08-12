"""A new themed command is one Lens entry here plus a subparser pointing at cmd_themed."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Lens:
    """A themed, pure-data search; blurb carries its own Rich markup."""

    keywords: list[str]
    created_range: str | None
    pushed: str | None
    header: str
    header_style: str
    blurb: str


THEMED_LENSES: dict[str, Lens] = {
    "morgue": Lens(
        keywords=["fork", "mirror", "deleted", "moved", "404", "gone"],
        created_range="2008-01-01..2016-12-31",
        pushed="<2018-01-01",
        header="Entering the morgue... dead forks and inactive repos",
        header_style="bold cyan",
        blurb="[dim]Repos marked as deleted, moved, or long abandoned[/dim]",
    ),
    "casket": Lens(
        keywords=[
            "archived",
            "unmaintained",
            "deprecated",
            "read-only",
            "no longer maintained",
        ],
        created_range=None,
        pushed="<2020-01-01",
        header="Opening the casket... archived and frozen repositories",
        header_style="bold cyan",
        blurb="[dim]Repos marked as archived, unmaintained, or deprecated[/dim]",
    ),
}
