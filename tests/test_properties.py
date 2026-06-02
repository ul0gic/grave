"""Property-based tests for the parsers and merge logic.

Hypothesis earns its place on the query builder (``build_search_query``) and
the date formatter: arbitrary input must either produce a well-formed result
or raise the one documented exception — never an unexpected exception.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any
from unittest.mock import MagicMock, patch

from hypothesis import given
from hypothesis import strategies as st

from grave.integrations import github
from grave.models.search import SearchSpec
from grave.services.query import build_search_query
from grave.view.display import _format_date

# --------------------------------------------------------------------------- #
# build_search_query
# --------------------------------------------------------------------------- #

_keyword_text = st.text(min_size=1).filter(lambda s: s.strip() != "")


@given(keywords=st.lists(_keyword_text, max_size=8))
def test_build_search_query_keywords_survive_unsplit(keywords: list[str]) -> None:
    spec = build_search_query(keywords=keywords)
    # Each keyword stays a single, distinct element — never split or merged.
    assert spec.keywords == keywords
    assert len(spec.keywords) == len(keywords)


@given(
    keywords=st.lists(_keyword_text, max_size=5),
    language=st.one_of(st.none(), st.text(min_size=1)),
    stars=st.one_of(st.none(), st.text(min_size=1)),
)
def test_build_search_query_qualifier_presence_is_order_stable(
    keywords: list[str], language: str | None, stars: str | None
) -> None:
    spec = build_search_query(keywords=keywords, language=language, stars_range=stars)
    qual_names = [name for name, _ in spec.qualifiers]
    # The build order is fixed: created, language, stars, pushed. Here only
    # language and stars may appear, and language must precede stars.
    if "language" in qual_names and "stars" in qual_names:
        assert qual_names.index("language") < qual_names.index("stars")


@given(keywords=st.lists(_keyword_text.filter(lambda s: " " not in s), max_size=6))
def test_build_search_query_display_reconstructs_keywords(keywords: list[str]) -> None:
    # For single-token keywords, display() round-trips back to the keyword list.
    spec = build_search_query(keywords=keywords)
    if keywords:
        assert spec.display().split(" ") == keywords
    else:
        assert spec.display() == ""


# --------------------------------------------------------------------------- #
# _format_date — never raises on arbitrary input
# --------------------------------------------------------------------------- #


@given(text=st.text())
def test_format_date_never_raises(text: str) -> None:
    result = _format_date(text)
    assert isinstance(result, str)
    # Either a YYYY-MM-DD shape or the sentinel.
    assert result == "N/A" or len(result) == 10


# --------------------------------------------------------------------------- #
# _multi_keyword_search — dedup + sort invariants under overlap
# --------------------------------------------------------------------------- #


def _make_run(per_keyword: dict[str, list[dict[str, Any]]]) -> Any:
    def fake_run(cmd: list[str], **_kwargs: Any) -> MagicMock:
        keyword = cmd[cmd.index("--limit") - 1]
        mock = MagicMock()
        mock.returncode = 0
        mock.stderr = ""
        mock.stdout = json.dumps(per_keyword.get(keyword, []))
        return mock

    return fake_run


@given(
    names=st.lists(
        st.sampled_from(["x/a", "x/b", "x/c", "x/d"]),
        min_size=1,
        max_size=4,
    ),
    # min_value=1 sidesteps the known _merge_sort_key 0-vs-"" defect (covered by
    # its own xfail in test_github.py); here we only assert dedup + sort invariants.
    stars=st.lists(st.integers(min_value=1, max_value=1000), min_size=1, max_size=4),
)
def test_multi_keyword_search_output_is_deduped_and_sorted(
    names: list[str], stars: list[int]
) -> None:
    # Two keywords share an overlapping pool of repo names.
    star_by_name = {name: stars[i % len(stars)] for i, name in enumerate(names)}
    pool = [{"fullName": n, "stargazersCount": s} for n, s in star_by_name.items()]
    per_keyword = {"k1": pool, "k2": list(reversed(pool))}

    spec = SearchSpec(keywords=["k1", "k2"], qualifiers=[])
    with patch.object(subprocess, "run", side_effect=_make_run(per_keyword)):
        result = github.search_repos(spec, limit=100, sort="stars")

    out_names = [r["full_name"] for r in result["items"]]
    # Deduped by full_name.
    assert len(out_names) == len(set(out_names))
    # Sorted by stars descending.
    out_stars = [r["stargazers_count"] for r in result["items"]]
    assert out_stars == sorted(out_stars, reverse=True)
