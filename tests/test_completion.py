"""Tests for the shell completion script generator."""

from __future__ import annotations

import subprocess
import sys

import pytest

from grave.cli.parser import main
from grave.config.presets import PRESETS


def run_cli(argv: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Invoke main() with a fake argv."""
    monkeypatch.setattr("sys.argv", ["grave", *argv])
    main()


def _completion_output(
    shell: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> str:
    run_cli(["completion", shell], monkeypatch)
    return capsys.readouterr().out


def test_bash_script_lists_commands_and_presets(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    out = _completion_output("bash", monkeypatch, capsys)
    assert "complete -F _grave grave" in out
    for command in ("scan", "dig", "rabbit-hole", "morgue", "casket", "completion"):
        assert command in out
    for preset in PRESETS:
        assert preset.name in out
    # Subcommand flags are embedded per-command.
    assert "--preset" in out
    assert "--abandoned" in out


def test_zsh_script_adds_bashcompinit_preamble(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    out = _completion_output("zsh", monkeypatch, capsys)
    assert "bashcompinit" in out
    assert "complete -F _grave grave" in out


def test_invalid_shell_exits_2(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(SystemExit) as exc:
        run_cli(["completion", "fish"], monkeypatch)
    assert exc.value.code == 2


def test_bash_script_is_valid_syntax(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    out = _completion_output("bash", monkeypatch, capsys)
    result = subprocess.run(
        ["bash", "-n"],
        input=out,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_completion_runs_via_module_entry_point() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "grave", "completion", "bash"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "complete -F _grave grave" in result.stdout
