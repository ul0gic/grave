"""Tests for grave.commands.init.cmd_init — interactive onboarding.

``cmd_init`` shells out to gh and prompts via input(); both are mocked at their
boundaries (subprocess.run, builtins.input). It creates no files — onboarding
only checks prerequisites.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from grave.cli.parser import main


def run_cli(argv: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["grave", *argv])
    main()


def _proc(returncode: int = 0, stdout: str = "", stderr: str = "") -> MagicMock:
    mock = MagicMock()
    mock.returncode = returncode
    mock.stdout = stdout
    mock.stderr = stderr
    return mock


def test_init_success_checks_prerequisites(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # gh --version, then gh auth status both succeed.
    def fake_run(cmd: list[str], **_kwargs: Any) -> MagicMock:
        if cmd[:2] == ["gh", "--version"]:
            return _proc(stdout="gh version 2.76.0 (2024-01-01)")
        if cmd[:3] == ["gh", "auth", "status"]:
            return _proc(stderr="✓ Logged in to github.com account ul0gic (keyring)")
        return _proc()

    with patch("grave.commands.init.subprocess.run", side_effect=fake_run):
        run_cli(["init"], monkeypatch)

    out = capsys.readouterr().out
    assert "gh authenticated as ul0gic" in out
    assert "You're ready to dig" in out


def test_init_gh_missing_exits_1(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with (
        patch("grave.commands.init.subprocess.run", side_effect=FileNotFoundError),
        pytest.raises(SystemExit) as exc,
    ):
        run_cli(["init"], monkeypatch)
    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "gh CLI not found" in out
    assert "Install gh CLI" in out


def test_init_unauthenticated_declined_exits_1(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fake_run(cmd: list[str], **_kwargs: Any) -> MagicMock:
        if cmd[:2] == ["gh", "--version"]:
            return _proc(stdout="gh version 2.76.0")
        if cmd[:3] == ["gh", "auth", "status"]:
            return _proc(returncode=1, stderr="not logged in")
        return _proc()

    with (
        patch("grave.commands.init.subprocess.run", side_effect=fake_run),
        patch("builtins.input", return_value="n"),
        pytest.raises(SystemExit) as exc,
    ):
        run_cli(["init"], monkeypatch)
    assert exc.value.code == 1
    assert "gh auth login" in capsys.readouterr().out


def test_init_unauthenticated_accepts_and_logs_in(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **_kwargs: Any) -> MagicMock:
        calls.append(cmd)
        if cmd[:2] == ["gh", "--version"]:
            return _proc(stdout="gh version 2.76.0")
        if cmd[:3] == ["gh", "auth", "status"]:
            return _proc(returncode=1, stderr="not logged in")
        if cmd[:3] == ["gh", "auth", "login"]:
            return _proc(returncode=0)
        return _proc()

    with (
        patch("grave.commands.init.subprocess.run", side_effect=fake_run),
        patch("builtins.input", return_value="y"),
    ):
        run_cli(["init"], monkeypatch)

    assert ["gh", "auth", "login"] in calls
    out = capsys.readouterr().out
    assert "Authentication successful" in out
    assert "You're ready to dig" in out
