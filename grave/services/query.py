"""Pure query-building service: parameters in, structured SearchSpec out.

No I/O and no subprocess. Builds the :class:`~grave.models.search.SearchSpec` consumed
by the gh integration layer, keeping keywords distinct from qualifiers.
"""

from __future__ import annotations

from grave.models.search import SearchSpec


def build_search_query(
    keywords: list[str] | None = None,
    created_range: str | None = None,
    language: str | None = None,
    stars_range: str | None = None,
    pushed: str | None = None,
) -> SearchSpec:
    """Build a structured search spec from parameters.

    Args:
        keywords: List of keywords to search for
        created_range: Date range for repository creation
            (e.g., '2008-01-01..2010-12-31')
        language: Programming language filter
        stars_range: Star count filter (e.g., '>100', '10..50', '>=1')
        pushed: Last push date filter (e.g., '<2015-01-01')

    Returns:
        A SearchSpec with keywords and qualifiers kept separate.

    Example:
        >>> spec = build_search_query(
        ...     keywords=["neural network", "utopia"],
        ...     created_range="2008-01-01..2012-12-31",
        ...     language="Python",
        ...     stars_range=">10",
        ... )
        >>> spec.display()
        'neural network utopia created:2008-01-01..2012-12-31 language:Python stars:>10'
    """
    qualifiers: list[tuple[str, str]] = []
    if created_range:
        qualifiers.append(("created", created_range))
    if language:
        qualifiers.append(("language", language))
    if stars_range:
        qualifiers.append(("stars", stars_range))
    if pushed:
        qualifiers.append(("pushed", pushed))

    return SearchSpec(keywords=list(keywords or []), qualifiers=qualifiers)
