"""Themed-lens definitions for the ``morgue`` and ``casket`` commands.

A *lens* is a pure-data search: a fixed set of keywords plus optional
created/pushed qualifiers and the themed banner shown above the results. Both
the morgue and the casket are the same generic search differing only in these
values, so they live here as one declarative table. Adding a future lens is a
single :class:`Lens` entry plus a subparser pointing at ``cmd_themed``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Lens:
    """A themed, pure-data search over abandoned repositories.

    Attributes:
        keywords: Fixed keywords for the search query.
        created_range: Optional creation date range (None means "any").
        pushed: Last-push qualifier marking abandonment (e.g. '<2018-01-01').
        header: Banner line printed above results (styled with ``header_style``).
        header_style: Rich style applied to the header line.
        blurb: Secondary line printed below the header (carries its own markup).
    """

    keywords: list[str]
    created_range: str | None
    pushed: str | None
    header: str
    header_style: str
    blurb: str


# Themed lenses keyed by command name. Each entry holds exactly the values the
# corresponding command renders; behavior lives in commands.themed.cmd_themed.
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
