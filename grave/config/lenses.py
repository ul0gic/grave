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
    stars_range: str | None = None
    archived: bool | None = None
    include_forks: str | None = None


THEMED_LENSES: dict[str, Lens] = {
    "morgue": Lens(
        keywords=[],
        created_range="2008-01-01..2016-12-31",
        pushed="<2018-01-01",
        stars_range=">=20",
        include_forks="only",
        header="Entering the morgue... dead forks and inactive repos",
        header_style="bold cyan",
        blurb="[dim]Forks that gathered stars, then stopped moving[/dim]",
    ),
    "casket": Lens(
        keywords=[],
        created_range=None,
        pushed="<2020-01-01",
        archived=True,
        header="Opening the casket... archived and frozen repositories",
        header_style="bold cyan",
        blurb="[dim]Repos their owners formally archived and walked away from[/dim]",
    ),
}
