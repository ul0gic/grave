"""Search preset data model.

Defines the :class:`Preset` dataclass: pure fields describing a curated search.
Query building lives in the CLI layer (which may depend on the API), so this
model imports nothing first-party and stays cycle-free.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Preset:
    """A curated search preset for GitHub repository discovery.

    Attributes:
        name: Unique identifier for the preset
        description: Human-readable description of what this preset finds
        keywords: Keywords to include in the search query
        created_range: Date range for repository creation (e.g., '2000..2010')
        language: Programming language filter (optional)
        stars_range: Star count filter (e.g., '>100', '10..50')
        pushed: Last push date filter (e.g., '<2015-01-01')
        category: Category grouping for the preset
        sort: Sort order for results ('stars', 'forks', 'updated')
    """

    name: str
    description: str
    keywords: list[str]
    created_range: str | None = None
    language: str | None = None
    stars_range: str | None = None
    pushed: str | None = None
    category: str = "general"
    sort: str = "stars"
