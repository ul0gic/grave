"""The ``grave init`` command: interactive onboarding and prerequisite checks."""

from __future__ import annotations

import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def cmd_init(args: argparse.Namespace) -> None:
    """Interactive onboarding with prerequisite checks."""
    from rich.console import Console

    console = Console()

    # Welcome banner
    console.print()
    console.print(
        "⚰️  GRAVE — Git Repository Abandonment & Vintage Explorer",
        style="bold cyan",
    )
    console.print()
    console.print("Let's get you set up for digital archaeology.")
    console.print()
    console.print("Checking prerequisites...", style="bold")
    console.print()

    all_checks_passed = True

    # Check 1: Python version
    python_version = sys.version_info
    if python_version >= (3, 10):
        py_ver = f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}"
        console.print(py_ver, style="green")
    else:
        py_ver = (
            f"✗ Python {python_version.major}."
            f"{python_version.minor}.{python_version.micro} (requires 3.10+)"
        )
        console.print(py_ver, style="red")
        all_checks_passed = False

    # Check 2: gh CLI installed
    gh_version = None
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            # Extract version from output like "gh version 2.76.0"
            version_line = result.stdout.split("\n")[0]
            parts = version_line.split()
            gh_version = parts[2] if len(parts) > 2 else "installed"
            console.print(f"✓ gh CLI {gh_version}", style="green")
        else:
            console.print("✗ gh CLI not found", style="red")
            all_checks_passed = False
    except FileNotFoundError:
        console.print("✗ gh CLI not found", style="red")
        all_checks_passed = False

    # Check 3: gh authenticated
    gh_authenticated = False
    gh_username = None
    if gh_version:
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                # Parse lines like "✓ Logged in to github.com account user"
                for line in result.stderr.split("\n"):
                    if "Logged in to github.com account" in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == "account" and i + 1 < len(parts):
                                gh_username = parts[i + 1]
                                break
                if gh_username:
                    msg = f"✓ gh authenticated as {gh_username}"
                    console.print(msg, style="green")
                    gh_authenticated = True
                else:
                    console.print("✓ gh authenticated", style="green")
                    gh_authenticated = True
            else:
                console.print("✗ gh not authenticated", style="red")
        except (subprocess.SubprocessError, FileNotFoundError):
            console.print("✗ gh not authenticated", style="red")

    console.print()

    # If gh is installed but not authenticated, offer to authenticate
    if gh_version and not gh_authenticated:
        try:
            prompt = "Would you like to authenticate now? [Y/n] "
            response = input(prompt).strip().lower()
            if response == "" or response == "y":
                console.print()
                console.print("Launching GitHub authentication...", style="bold")
                console.print()
                # Run gh auth login with inherited stdio
                login_result = subprocess.run(
                    ["gh", "auth", "login"],
                    stdin=sys.stdin,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                )
                if login_result.returncode == 0:
                    console.print()
                    console.print("✓ Authentication successful", style="green")
                    gh_authenticated = True
                else:
                    console.print()
                    console.print("✗ Authentication failed", style="red")
                    all_checks_passed = False
            else:
                console.print()
                msg = "Run 'gh auth login' when you're ready."
                console.print(msg, style="yellow")
                all_checks_passed = False
        except (EOFError, KeyboardInterrupt):
            console.print()
            console.print("Authentication cancelled.", style="yellow")
            all_checks_passed = False

    # If any check failed, exit
    if not all_checks_passed or not gh_authenticated:
        console.print()
        msg = "Setup incomplete. Please resolve the issues above."
        console.print(msg, style="red bold")
        console.print()
        if not gh_version:
            console.print("Install gh CLI: https://cli.github.com", style="dim")
        console.print()
        sys.exit(1)

    console.print()
    console.print("You're ready to dig. Try:", style="bold")
    console.print("  [bold]grave scan --preset ancient[/bold]")
    console.print('  [bold]grave scan --keyword "fractal" --abandoned 10[/bold]')
    console.print("  [bold]grave presets[/bold]")
    console.print()
