"""Tests for the interactive result picker."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

from grave.commands.pick import prompt_dig

ITEMS: list[Any] = [
    {"full_name": "owner/first"},
    {"full_name": "owner/second"},
]


def _tty(value: bool) -> Any:
    return patch("sys.stdin.isatty", return_value=value)


def _tty_out(value: bool) -> Any:
    return patch("sys.stdout.isatty", return_value=value)


def test_prompt_skipped_when_not_a_tty() -> None:
    with (
        _tty(False),
        _tty_out(False),
        patch("grave.integrations.github.get_repo") as get_repo,
        patch("builtins.input", side_effect=AssertionError("input must not be called")),
    ):
        prompt_dig(ITEMS)
    get_repo.assert_not_called()


def test_prompt_skipped_for_empty_results() -> None:
    with (
        _tty(True),
        _tty_out(True),
        patch("builtins.input", side_effect=AssertionError("input must not be called")),
    ):
        prompt_dig([])


def test_valid_number_digs_that_repo() -> None:
    with (
        _tty(True),
        _tty_out(True),
        patch("builtins.input", side_effect=["2", ""]),
        patch(
            "grave.integrations.github.get_repo",
            return_value={"full_name": "owner/second"},
        ) as get_repo,
        patch("grave.view.display.display_repo_detail") as display,
    ):
        prompt_dig(ITEMS)
    get_repo.assert_called_once_with("owner", "second")
    display.assert_called_once()


def test_invalid_input_reprompts_then_exits(capsys: Any) -> None:
    with (
        _tty(True),
        _tty_out(True),
        patch("builtins.input", side_effect=["99", "abc", ""]),
        patch("grave.integrations.github.get_repo") as get_repo,
    ):
        prompt_dig(ITEMS)
    get_repo.assert_not_called()
    assert "between 1 and 2" in capsys.readouterr().out


def test_eof_exits_cleanly() -> None:
    with (
        _tty(True),
        _tty_out(True),
        patch("builtins.input", side_effect=EOFError),
        patch("grave.integrations.github.get_repo") as get_repo,
    ):
        prompt_dig(ITEMS)
    get_repo.assert_not_called()
