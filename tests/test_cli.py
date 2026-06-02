"""Tests for grave.cli — exit codes and output routing are part of the contract.

The gh boundary is mocked by patching the API functions the CLI imports
(``check_gh_auth``, ``search_repos``, ``get_repo``). No network, no real gh.
grave is stateless, so there is nothing to isolate on disk.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest

from grave.cli.parser import main

if TYPE_CHECKING:
    from collections.abc import Sequence


def run_cli(argv: Sequence[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Invoke main() with a fake argv."""
    monkeypatch.setattr("sys.argv", ["grave", *argv])
    main()


def _search_items(*names: str) -> dict[str, list[dict[str, Any]]]:
    items = [
        {
            "full_name": n,
            "description": "d",
            "stargazers_count": 1,
            "forks_count": 0,
            "watchers_count": 0,
            "open_issues_count": 0,
            "language": "Python",
            "created_at": "2010-01-01T00:00:00Z",
            "pushed_at": "2015-01-01T00:00:00Z",
            "updated_at": "2016-01-01T00:00:00Z",
            "topics": [],
            "html_url": f"https://github.com/{n}",
        }
        for n in names
    ]
    return {"items": items}


# --------------------------------------------------------------------------- #
# no command / help
# --------------------------------------------------------------------------- #


def test_no_command_prints_help_and_exits_zero(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as exc:
        run_cli([], monkeypatch)
    assert exc.value.code == 0
    assert "usage" in capsys.readouterr().out.lower()


# --------------------------------------------------------------------------- #
# scan — usage errors (exit 2) and preset resolution
# --------------------------------------------------------------------------- #


def test_scan_no_params_exits_2(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        pytest.raises(SystemExit) as exc,
    ):
        run_cli(["scan"], monkeypatch)
    assert exc.value.code == 2
    assert "at least one search parameter" in capsys.readouterr().err


def test_scan_preset_not_found_exits_2(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        pytest.raises(SystemExit) as exc,
    ):
        run_cli(["scan", "--preset", "nonexistent"], monkeypatch)
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "not found" in err
    assert "Available presets" in err


def test_scan_abandoned_negative_exits_2(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        pytest.raises(SystemExit) as exc,
    ):
        run_cli(["scan", "--keyword", "x", "--abandoned", "-5"], monkeypatch)
    assert exc.value.code == 2
    assert "invalid --abandoned" in capsys.readouterr().err


def test_scan_dead_since_out_of_range_exits_2(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        pytest.raises(SystemExit) as exc,
    ):
        run_cli(["scan", "--keyword", "x", "--dead-since", "99999"], monkeypatch)
    assert exc.value.code == 2
    assert "invalid --dead-since" in capsys.readouterr().err


def test_scan_abandoned_zero_is_honored(monkeypatch: pytest.MonkeyPatch) -> None:
    # M3 regression: --abandoned 0 must produce a pushed:<thisyear filter,
    # not be silently dropped (0 is falsy but still a valid request).
    import datetime

    this_year = datetime.date.today().year
    captured: dict[str, Any] = {}

    def fake_search(spec: Any, limit: int = 30, sort: Any = None) -> dict[str, Any]:
        captured["spec"] = spec
        return {"items": []}

    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.search_repos", side_effect=fake_search),
    ):
        run_cli(["scan", "--keyword", "x", "--abandoned", "0"], monkeypatch)

    qualifiers = dict(captured["spec"].qualifiers)
    assert qualifiers["pushed"] == f"<{this_year}-01-01"


def test_scan_preset_passes_sort_through(monkeypatch: pytest.MonkeyPatch) -> None:
    # H3 regression: the 'forgotten' preset sorts by 'updated'; that sort key
    # must reach search_repos, not be replaced by the --sort default of 'stars'.
    captured: dict[str, Any] = {}

    def fake_search(spec: Any, limit: int = 30, sort: Any = None) -> dict[str, Any]:
        captured["sort"] = sort
        return {"items": []}

    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.search_repos", side_effect=fake_search),
    ):
        run_cli(["scan", "--preset", "forgotten"], monkeypatch)

    assert captured["sort"] == "updated"


def test_scan_custom_sort_passed_through(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_search(spec: Any, limit: int = 30, sort: Any = None) -> dict[str, Any]:
        captured["sort"] = sort
        captured["limit"] = limit
        return {"items": []}

    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.search_repos", side_effect=fake_search),
    ):
        run_cli(["scan", "--keyword", "x", "--sort", "forks", "--limit", "7"], monkeypatch)

    assert captured["sort"] == "forks"
    assert captured["limit"] == 7


def test_scan_json_output_is_valid_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.search_repos", return_value=_search_items("a/b", "c/d")),
    ):
        run_cli(["scan", "--keyword", "x", "--json"], monkeypatch)
    payload = json.loads(capsys.readouterr().out)
    assert [r["full_name"] for r in payload] == ["a/b", "c/d"]


def test_scan_unauthenticated_exits_1(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # check_gh_auth now raises; the dispatch catch turns GhError into exit 1.
    from grave.integrations.github import GhAuthError

    with (
        patch(
            "grave.integrations.github.check_gh_auth",
            side_effect=GhAuthError("GitHub authentication required."),
        ),
        pytest.raises(SystemExit) as exc,
    ):
        run_cli(["scan", "--keyword", "x"], monkeypatch)
    assert exc.value.code == 1
    assert "grave: error:" in capsys.readouterr().err


def test_scan_gh_error_exits_1_via_dispatch(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # A GhError raised mid-search propagates to the dispatch catch in main().
    from grave.integrations.github import GhError

    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch(
            "grave.integrations.github.search_repos",
            side_effect=GhError("gh blew up"),
        ),
        pytest.raises(SystemExit) as exc,
    ):
        run_cli(["scan", "--keyword", "x"], monkeypatch)
    assert exc.value.code == 1
    assert "grave: error: gh blew up" in capsys.readouterr().err


def test_scan_preset_language_override(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_search(spec: Any, limit: int = 30, sort: Any = None) -> dict[str, Any]:
        captured["spec"] = spec
        return {"items": []}

    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.search_repos", side_effect=fake_search),
    ):
        run_cli(["scan", "--preset", "dead-lang", "--language", "Perl"], monkeypatch)

    qualifiers = dict(captured["spec"].qualifiers)
    assert qualifiers["language"] == "Perl"


# --------------------------------------------------------------------------- #
# dig / rabbit-hole — owner/repo validation
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("bad", ["noslash", "a/b/c", "/leading", "trailing/", "/"])
def test_dig_bad_repo_format_exits_2(
    bad: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        pytest.raises(SystemExit) as exc,
    ):
        run_cli(["dig", bad], monkeypatch)
    assert exc.value.code == 2
    assert "invalid repository format" in capsys.readouterr().err


def test_dig_json_output(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = {"full_name": "torvalds/linux", "stargazers_count": 1, "topics": []}
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.get_repo", return_value=repo),
    ):
        run_cli(["dig", "torvalds/linux", "--json"], monkeypatch)
    payload = json.loads(capsys.readouterr().out)
    assert payload["full_name"] == "torvalds/linux"


def test_rabbit_hole_bad_repo_exits_2(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        pytest.raises(SystemExit) as exc,
    ):
        run_cli(["rabbit-hole", "noslash"], monkeypatch)
    assert exc.value.code == 2
    assert "invalid repository format" in capsys.readouterr().err


def test_rabbit_hole_builds_spec_from_repo(monkeypatch: pytest.MonkeyPatch) -> None:
    repo = {
        "full_name": "owner/repo",
        "language": "Python",
        "created_at": "2010-04-10T00:00:00Z",
        "topics": ["cli", "tool", "archive", "extra"],
    }
    captured: dict[str, Any] = {}

    def fake_search(spec: Any, limit: int = 30, sort: Any = None) -> dict[str, Any]:
        captured["spec"] = spec
        return {"items": []}

    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.get_repo", return_value=repo),
        patch("grave.integrations.github.search_repos", side_effect=fake_search),
    ):
        run_cli(["rabbit-hole", "owner/repo", "--json"], monkeypatch)

    spec = captured["spec"]
    # Up to 3 shared topics become keywords; language + ±2yr created window.
    assert spec.keywords == ["cli", "tool", "archive"]
    qualifiers = dict(spec.qualifiers)
    assert qualifiers["language"] == "Python"
    assert qualifiers["created"] == "2008-01-01..2012-12-31"


# --------------------------------------------------------------------------- #
# presets
# --------------------------------------------------------------------------- #


def test_presets_lists_all(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run_cli(["presets"], monkeypatch)
    out = capsys.readouterr().out
    assert "Available Search Presets" in out
    assert "ancient" in out


def test_presets_valid_category(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run_cli(["presets", "--category", "archaeology"], monkeypatch)
    out = capsys.readouterr().out
    assert "ancient" in out


def test_presets_invalid_category_exits_2(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as exc:
        run_cli(["presets", "--category", "bogus"], monkeypatch)
    assert exc.value.code == 2
    assert "invalid category" in capsys.readouterr().err


# --------------------------------------------------------------------------- #
# export
# --------------------------------------------------------------------------- #


def test_export_json_from_api(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.search_repos", return_value=_search_items("a/b")),
    ):
        run_cli(["export", "--keyword", "x", "--format", "json"], monkeypatch)
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["full_name"] == "a/b"


def test_export_ndjson_one_object_per_line(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.search_repos", return_value=_search_items("a/b", "c/d")),
    ):
        run_cli(["export", "--keyword", "x", "--format", "ndjson"], monkeypatch)
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.strip()]
    assert len(lines) == 2
    assert json.loads(lines[0])["full_name"] == "a/b"
    assert json.loads(lines[1])["full_name"] == "c/d"


def test_export_csv_has_header_and_rows(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.search_repos", return_value=_search_items("a/b")),
    ):
        run_cli(["export", "--keyword", "x", "--format", "csv"], monkeypatch)
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("full_name,description,language")
    assert out[1].startswith("a/b,")


def test_export_csv_empty_emits_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.search_repos", return_value={"items": []}),
    ):
        run_cli(["export", "--keyword", "x", "--format", "csv"], monkeypatch)
    assert capsys.readouterr().out == ""


def test_export_no_params_exits_2(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        pytest.raises(SystemExit) as exc,
    ):
        run_cli(["export", "--format", "json"], monkeypatch)
    assert exc.value.code == 2


# --------------------------------------------------------------------------- #
# random / morgue / casket — preset and themed searches
# --------------------------------------------------------------------------- #


def test_random_runs_with_a_preset(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.search_repos", return_value=_search_items("rand/repo")),
    ):
        run_cli(["random", "--json"], monkeypatch)
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["full_name"] == "rand/repo"


def test_morgue_uses_fork_keywords(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_search(spec: Any, limit: int = 30, sort: Any = None) -> dict[str, Any]:
        captured["spec"] = spec
        return {"items": []}

    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.search_repos", side_effect=fake_search),
    ):
        run_cli(["morgue", "--json"], monkeypatch)

    assert "fork" in captured["spec"].keywords
    assert dict(captured["spec"].qualifiers)["pushed"] == "<2018-01-01"


def test_casket_applies_language_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_search(spec: Any, limit: int = 30, sort: Any = None) -> dict[str, Any]:
        captured["spec"] = spec
        return {"items": []}

    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.search_repos", side_effect=fake_search),
    ):
        run_cli(["casket", "--language", "Ruby", "--json"], monkeypatch)

    assert dict(captured["spec"].qualifiers)["language"] == "Ruby"


# --------------------------------------------------------------------------- #
# themed commands — non-JSON (Rich table) output paths
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("argv", "banner"),
    [
        (["random"], "Random dig with preset"),
        (["morgue"], "Entering the morgue"),
        (["casket"], "Opening the casket"),
    ],
)
def test_themed_commands_render_table(
    argv: list[str],
    banner: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.search_repos", return_value=_search_items("themed/repo")),
    ):
        run_cli(argv, monkeypatch)
    out = capsys.readouterr().out
    assert banner in out
    assert "themed/repo" in out


def test_rabbit_hole_renders_table(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = {
        "full_name": "owner/repo",
        "language": "Python",
        "created_at": "2010-04-10T00:00:00Z",
        "topics": ["cli"],
    }
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.get_repo", return_value=repo),
        patch("grave.integrations.github.search_repos", return_value=_search_items("similar/repo")),
    ):
        run_cli(["rabbit-hole", "owner/repo"], monkeypatch)
    out = capsys.readouterr().out
    assert "rabbit hole" in out.lower()
    assert "similar/repo" in out


def test_scan_renders_table_when_not_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.search_repos", return_value=_search_items("table/repo")),
    ):
        run_cli(["scan", "--keyword", "x"], monkeypatch)
    out = capsys.readouterr().out
    assert "table/repo" in out
    assert "Found 1 repositories" in out


def test_dig_open_launches_browser(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = {"full_name": "a/b", "html_url": "https://github.com/a/b", "topics": []}
    with (
        patch("grave.integrations.github.check_gh_auth", return_value=None),
        patch("grave.integrations.github.get_repo", return_value=repo),
        patch("webbrowser.open") as wb,
    ):
        run_cli(["dig", "a/b", "--open"], monkeypatch)
    wb.assert_called_once_with("https://github.com/a/b")
    assert "Opening" in capsys.readouterr().out
