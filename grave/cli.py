"""CLI entry point and argument parsing for grave."""

import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

from grave import __version__

# Era mapping for --era flag
ERAS = {
    "y2k": ("1999-01-01", "2003-12-31"),
    "dotcom": ("1997-01-01", "2001-12-31"),
    "web2.0": ("2004-01-01", "2009-12-31"),
    "early-github": ("2008-01-01", "2011-12-31"),
    "pre-mobile": ("2007-01-01", "2010-12-31"),
}


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
        py_ver = (
            f"✓ Python {python_version.major}."
            f"{python_version.minor}.{python_version.micro}"
        )
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
                # Extract username from output
                for line in result.stderr.split("\n"):
                    if "Logged in to github.com account" in line or "as" in line:
                        parts = line.split()
                        if len(parts) > 0:
                            # "✓ Logged in to github.com account user"
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
        except Exception:
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
                result = subprocess.run(
                    ["gh", "auth", "login"],
                    stdin=sys.stdin,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                )
                if result.returncode == 0:
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

    # Create data directory
    data_home = os.environ.get("XDG_DATA_HOME")
    if data_home:
        data_dir = Path(data_home) / "grave"
    else:
        data_dir = Path.home() / ".local" / "share" / "grave"

    data_dir.mkdir(parents=True, exist_ok=True)

    console.print()
    console.print(f"✓ Data directory ready: {data_dir}", style="green")
    console.print()
    console.print("You're ready to dig. Try:", style="bold")
    console.print("  [bold]grave scan --preset ancient[/bold]")
    console.print("  [bold]grave scan --keyword \"fractal\" --abandoned 10[/bold]")
    console.print("  [bold]grave presets[/bold]")
    console.print()


def cmd_presets(args: argparse.Namespace) -> None:
    """List all available preset search profiles."""
    from grave.display import display_presets
    from grave.presets import list_categories, list_presets

    try:
        # Validate category if provided
        if args.category:
            available_categories = list_categories()
            if args.category not in available_categories:
                print(
                    f"grave: error: invalid category '{args.category}'",
                    file=sys.stderr,
                )
                print(
                    f"Available categories: {', '.join(available_categories)}",
                    file=sys.stderr,
                )
                sys.exit(2)

        # Get presets (filtered by category if provided)
        presets = list_presets(category=args.category)
        display_presets(presets, category=args.category)
    except Exception as e:
        print(f"grave: error: failed to list presets: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_scan(args: argparse.Namespace) -> None:
    """Run a repository scan with preset or custom parameters."""
    from grave.api import build_search_query, check_gh_auth, search_repos
    from grave.display import display_results
    from grave.presets import get_preset, list_presets

    # Pre-flight check: verify gh CLI is authenticated
    if not check_gh_auth():
        sys.exit(1)

    try:
        # Branch: preset mode or custom search mode
        if args.preset:
            # PRESET MODE: Get the preset by name
            preset = get_preset(args.preset)
            if preset is None:
                print(
                    f"grave: error: preset '{args.preset}' not found",
                    file=sys.stderr,
                )
                print("\nAvailable presets:", file=sys.stderr)
                for p in list_presets():
                    print(f"  - {p.name}", file=sys.stderr)
                sys.exit(1)

            # Build query with overrides from CLI flags
            # If overrides are provided, rebuild the query with them
            if args.language or args.stars:
                query = build_search_query(
                    keywords=preset.keywords if preset.keywords else None,
                    created_range=preset.created_range,
                    language=args.language if args.language else preset.language,
                    stars_range=args.stars if args.stars else preset.stars_range,
                )
            else:
                query = preset.build_query()

            # Execute search (sort is not customizable in preset mode)
            response = search_repos(query, limit=args.limit)
            items = response.get("items", [])

        else:
            # CUSTOM SEARCH MODE: Validate parameters
            if not any(
                [
                    args.keyword,
                    args.created,
                    args.pushed,
                    args.language,
                    args.stars,
                    args.abandoned,
                    args.era,
                    args.dead_since,
                ]
            ):
                print(
                    "grave: error: at least one search parameter "
                    "is required (or use --preset)",
                    file=sys.stderr,
                )
                print(
                    "Usage: grave scan [--preset <name>] "
                    "[--keyword <word>] [--created <range>] "
                    "[--pushed <range>] [--language <lang>] "
                    "[--stars <range>] [--abandoned <years>] [--era <name>]",
                    file=sys.stderr,
                )
                sys.exit(2)

            # Handle --era flag (takes precedence over --created)
            created_filter = args.created
            if args.era:
                start_date, end_date = ERAS[args.era]
                created_filter = f"{start_date}..{end_date}"

            # Handle pushed filters with precedence:
            # --dead-since > --abandoned > --pushed
            pushed_filter = args.pushed
            if args.dead_since:
                pushed_filter = f"<{args.dead_since}-01-01"
            elif args.abandoned:
                cutoff_year = date.today().year - args.abandoned
                pushed_filter = f"<{cutoff_year}-01-01"

            # Build search query
            query = build_search_query(
                keywords=args.keyword,
                created_range=created_filter,
                language=args.language,
                stars_range=args.stars,
                pushed=pushed_filter,
            )

            # Execute search with sort parameter
            response = search_repos(query, limit=args.limit, sort=args.sort)
            items = response.get("items", [])

        # Save scan results to database
        try:
            from grave import db

            conn = db.init_db()
            preset_name = args.preset if args.preset else None
            db.save_scan(conn, query, preset_name, items)
            conn.close()
        except Exception as e:
            # Don't crash on db save failure, just warn
            print(
                f"grave: warning: failed to save scan to database: {e}",
                file=sys.stderr,
            )

        # Display results
        if args.json:
            print(json.dumps(items, indent=2))
        else:
            display_results(items)

    except RuntimeError:
        # API errors already print to stderr
        sys.exit(1)
    except Exception as e:
        print(f"grave: error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_dig(args: argparse.Namespace) -> None:
    """Dig up detailed information about a repository."""
    from grave.api import check_gh_auth, get_repo
    from grave.display import display_repo_detail

    # Pre-flight check: verify gh CLI is authenticated
    if not check_gh_auth():
        sys.exit(1)

    try:
        # Parse owner/repo format
        parts = args.repo.split("/")
        if len(parts) != 2:
            print(
                f"grave: error: invalid repository format '{args.repo}'",
                file=sys.stderr,
            )
            print(
                "Expected format: owner/repo (e.g., 'torvalds/linux')",
                file=sys.stderr,
            )
            sys.exit(2)

        owner, repo = parts

        # Fetch repository details
        repo_data = get_repo(owner, repo)

        # Save to database
        try:
            from grave import db

            conn = db.init_db()
            db.save_repo(conn, repo_data)
            conn.close()
        except Exception as e:
            # Don't crash on db save failure, just warn
            print(
                f"grave: warning: failed to save repo to database: {e}",
                file=sys.stderr,
            )

        # Display detailed information
        if args.json:
            print(json.dumps(repo_data, indent=2))
        else:
            display_repo_detail(repo_data)

        # Open in browser if requested
        if args.open:
            import webbrowser

            url = repo_data.get("html_url")
            if url:
                print(f"Opening {url} in browser...")
                webbrowser.open(url)

    except RuntimeError:
        # API errors already print to stderr
        sys.exit(1)
    except Exception as e:
        print(f"grave: error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    """List all repositories from the database."""
    from grave import db
    from grave.display import display_results

    try:
        conn = db.init_db()

        # Fetch repos with filters
        repos = db.list_repos(
            conn,
            language=args.language,
            stars=args.stars,
            preset=args.preset,
            since=args.since,
            limit=args.limit,
        )
        conn.close()

        # Check if database is empty
        if not repos:
            from rich.console import Console

            console = Console()
            console.print()
            console.print(
                "No repos collected yet. Run 'grave scan' to start digging.",
                style="yellow",
            )
            console.print()
            return

        # Display results
        if args.json:
            print(json.dumps(repos, indent=2))
        else:
            display_results(repos)

    except Exception as e:
        print(f"grave: error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_db(args: argparse.Namespace) -> None:
    """Database management commands."""

    # Route to sub-subcommand
    if args.db_command == "stats":
        _cmd_db_stats()
    elif args.db_command == "path":
        _cmd_db_path()
    elif args.db_command == "clear":
        _cmd_db_clear(args)
    elif args.db_command == "vacuum":
        _cmd_db_vacuum()
    else:
        # No subcommand given, print help
        print("grave: error: db command requires a subcommand", file=sys.stderr)
        print("Available subcommands: stats, path, clear, vacuum", file=sys.stderr)
        sys.exit(2)


def _cmd_db_stats() -> None:
    """Show database statistics."""
    from rich.console import Console
    from rich.table import Table

    from grave import db

    try:
        conn = db.init_db()
        stats = db.get_db_stats(conn)
        conn.close()

        console = Console()

        # Format size
        size_bytes = stats["db_size"]
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes / 1024:.2f} KB"
        else:
            size_str = f"{size_bytes / (1024 * 1024):.2f} MB"

        # Overall stats
        console.print()
        console.print("[bold]Database Statistics[/bold]")
        console.print()
        console.print(f"Total repositories: {stats['total_repos']}")
        console.print(f"Total scans: {stats['total_scans']}")
        console.print(f"Database size: {size_str}")

        if stats["oldest_first_seen"]:
            from grave.display import _format_date

            oldest = _format_date(stats["oldest_first_seen"])
            newest = _format_date(stats["newest_first_seen"])
            console.print(f"Oldest repo first seen: {oldest}")
            console.print(f"Newest repo first seen: {newest}")

        # Top languages
        if stats["top_languages"]:
            console.print()
            console.print("[bold]Top 5 Languages[/bold]")
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Language", style="yellow")
            table.add_column("Count", justify="right")

            for lang in stats["top_languages"]:
                table.add_row(lang["language"], str(lang["count"]))

            console.print(table)

        console.print()

    except Exception as e:
        print(f"grave: error: {e}", file=sys.stderr)
        sys.exit(1)


def _cmd_db_path() -> None:
    """Print database file path."""
    from grave import db

    print(db.get_db_path())


def _cmd_db_clear(args: argparse.Namespace) -> None:
    """Clear database data."""
    from rich.console import Console

    from grave import db

    console = Console()

    # Check for confirmation flag
    if not args.confirm:
        console.print()
        console.print(
            "[yellow]Warning: This will delete data from the database.[/yellow]"
        )
        if args.scans:
            console.print("This will clear: scan history (scans + scan_repos tables)")
            console.print("Repositories will be preserved.")
        else:
            console.print("This will clear: ALL data (scans, repos, tags)")
        console.print()
        console.print("To confirm, run with --confirm flag:")
        if args.scans:
            console.print("  [bold]grave db clear --scans --confirm[/bold]")
        else:
            console.print("  [bold]grave db clear --confirm[/bold]")
        console.print()
        return

    try:
        conn = db.init_db()

        if args.scans:
            db.clear_scans(conn)
            console.print()
            console.print("[green]✓ Scan history cleared[/green]")
            console.print()
        else:
            db.clear_all(conn)
            console.print()
            console.print("[green]✓ All data cleared[/green]")
            console.print()

        conn.close()

    except Exception as e:
        print(f"grave: error: {e}", file=sys.stderr)
        sys.exit(1)


def _cmd_db_vacuum() -> None:
    """Vacuum the database to compact it."""
    from rich.console import Console

    from grave import db

    console = Console()

    try:
        db_path = db.get_db_path()

        # Get size before
        size_before = db_path.stat().st_size if db_path.exists() else 0

        conn = db.init_db()
        db.vacuum_db(conn)
        conn.close()

        # Get size after
        size_after = db_path.stat().st_size if db_path.exists() else 0

        # Format sizes
        def fmt_size(size_bytes: int) -> str:
            if size_bytes < 1024:
                return f"{size_bytes} B"
            if size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.2f} KB"
            return f"{size_bytes / (1024 * 1024):.2f} MB"

        console.print()
        console.print("[green]✓ Database vacuumed[/green]")
        console.print(f"Size before: {fmt_size(size_before)}")
        console.print(f"Size after: {fmt_size(size_after)}")
        saved = size_before - size_after
        if saved > 0:
            console.print(f"Saved: {fmt_size(saved)}", style="green")
        console.print()

    except Exception as e:
        print(f"grave: error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_random(args: argparse.Namespace) -> None:
    """Pick a random preset and discover something unexpected."""
    import random

    from grave.api import check_gh_auth, search_repos
    from grave.display import display_results
    from grave.presets import PRESETS

    # Pre-flight check: verify gh CLI is authenticated
    if not check_gh_auth():
        sys.exit(1)

    try:
        # Pick a random preset
        preset = random.choice(PRESETS)

        # Build query
        query = preset.build_query()

        # Execute search
        response = search_repos(query, limit=args.limit)
        items = response.get("items", [])

        # Save scan results to database
        try:
            from grave import db

            conn = db.init_db()
            db.save_scan(conn, query, preset.name, items)
            conn.close()
        except Exception as e:
            # Don't crash on db save failure, just warn
            print(
                f"grave: warning: failed to save scan to database: {e}",
                file=sys.stderr,
            )

        # Display results with a fun header
        if args.json:
            print(json.dumps(items, indent=2))
        else:
            from rich.console import Console

            console = Console()
            console.print()
            console.print(
                f"Random dig with preset: [bold cyan]{preset.name}[/bold cyan]",
                style="bold",
            )
            console.print(f"[dim]{preset.description}[/dim]")
            console.print()
            display_results(items)

    except RuntimeError:
        # API errors already print to stderr
        sys.exit(1)
    except Exception as e:
        print(f"grave: error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_rabbit_hole(args: argparse.Namespace) -> None:
    """Find repos similar to a given repository."""
    from grave.api import build_search_query, check_gh_auth, get_repo, search_repos
    from grave.display import display_results

    # Pre-flight check: verify gh CLI is authenticated
    if not check_gh_auth():
        sys.exit(1)

    try:
        # Parse owner/repo format
        parts = args.repo.split("/")
        if len(parts) != 2:
            print(
                f"grave: error: invalid repository format '{args.repo}'",
                file=sys.stderr,
            )
            print(
                "Expected format: owner/repo (e.g., 'torvalds/linux')",
                file=sys.stderr,
            )
            sys.exit(2)

        owner, repo = parts

        # Fetch repository details
        repo_data = get_repo(owner, repo)

        # Extract relevant fields
        language = repo_data.get("language")
        created_at = repo_data.get("created_at", "")
        topics = repo_data.get("topics", [])

        # Parse created_at to get year
        created_year = None
        if created_at:
            # created_at is in ISO format: "2008-04-10T12:34:56Z"
            created_year = int(created_at.split("-")[0])

        # Build search query for similar repos
        # Use language, similar creation date (±2 years), and topics
        keywords = []
        if topics:
            # Pick up to 3 topics as keywords
            keywords = topics[:3]

        created_range = None
        if created_year:
            start_year = created_year - 2
            end_year = created_year + 2
            created_range = f"{start_year}-01-01..{end_year}-12-31"

        query = build_search_query(
            keywords=keywords if keywords else None,
            created_range=created_range,
            language=language,
        )

        # Execute search
        response = search_repos(query, limit=args.limit)
        items = response.get("items", [])

        # Save scan results to database
        try:
            from grave import db

            conn = db.init_db()
            db.save_scan(conn, query, None, items)
            conn.close()
        except Exception as e:
            # Don't crash on db save failure, just warn
            print(
                f"grave: warning: failed to save scan to database: {e}",
                file=sys.stderr,
            )

        # Display results with a fun header
        if args.json:
            print(json.dumps(items, indent=2))
        else:
            from rich.console import Console

            console = Console()
            console.print()
            console.print(
                f"Down the rabbit hole from [bold cyan]{args.repo}[/bold cyan]...",
                style="bold",
            )
            if language:
                console.print(f"[dim]Language: {language}[/dim]")
            if created_year:
                console.print(f"[dim]Created: {created_year} (±2 years)[/dim]")
            if topics:
                console.print(f"[dim]Topics: {', '.join(topics[:3])}[/dim]")
            console.print()
            display_results(items)

    except RuntimeError:
        # API errors already print to stderr
        sys.exit(1)
    except Exception as e:
        print(f"grave: error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_morgue(args: argparse.Namespace) -> None:
    """Search for dead forks and repos with inactive owners."""
    from grave.api import build_search_query, check_gh_auth, search_repos
    from grave.display import display_results

    # Pre-flight check: verify gh CLI is authenticated
    if not check_gh_auth():
        sys.exit(1)

    try:
        # Build search query for dead forks and inactive repos
        # Using keywords: fork, mirror, deleted, moved, 404, gone
        # With old created dates and very old pushed dates
        keywords = ["fork", "mirror", "deleted", "moved", "404", "gone"]
        created_range = "2008-01-01..2016-12-31"
        pushed = "<2018-01-01"

        query = build_search_query(
            keywords=keywords,
            created_range=created_range,
            pushed=pushed,
        )

        # Execute search
        response = search_repos(query, limit=args.limit)
        items = response.get("items", [])

        # Save scan results to database
        try:
            from grave import db

            conn = db.init_db()
            db.save_scan(conn, query, None, items)
            conn.close()
        except Exception as e:
            # Don't crash on db save failure, just warn
            print(
                f"grave: warning: failed to save scan to database: {e}",
                file=sys.stderr,
            )

        # Display results with a thematic header
        if args.json:
            print(json.dumps(items, indent=2))
        else:
            from rich.console import Console

            console = Console()
            console.print()
            console.print(
                "Entering the morgue... dead forks and inactive repos",
                style="bold cyan",
            )
            console.print(
                "[dim]Repos marked as deleted, moved, or long abandoned[/dim]"
            )
            console.print()
            display_results(items)

    except RuntimeError:
        # API errors already print to stderr
        sys.exit(1)
    except Exception as e:
        print(f"grave: error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_casket(args: argparse.Namespace) -> None:
    """Search for archived and frozen repositories."""
    from grave.api import build_search_query, check_gh_auth, search_repos
    from grave.display import display_results

    # Pre-flight check: verify gh CLI is authenticated
    if not check_gh_auth():
        sys.exit(1)

    try:
        # Build search query for archived/frozen repos
        # Using keywords: archived, unmaintained, deprecated, read-only,
        # no longer maintained
        keywords = [
            "archived",
            "unmaintained",
            "deprecated",
            "read-only",
            "no longer maintained",
        ]
        pushed = "<2020-01-01"

        query = build_search_query(
            keywords=keywords,
            language=args.language,
            pushed=pushed,
        )

        # Execute search
        response = search_repos(query, limit=args.limit)
        items = response.get("items", [])

        # Save scan results to database
        try:
            from grave import db

            conn = db.init_db()
            db.save_scan(conn, query, None, items)
            conn.close()
        except Exception as e:
            # Don't crash on db save failure, just warn
            print(
                f"grave: warning: failed to save scan to database: {e}",
                file=sys.stderr,
            )

        # Display results with a thematic header
        if args.json:
            print(json.dumps(items, indent=2))
        else:
            from rich.console import Console

            console = Console()
            console.print()
            console.print(
                "Opening the casket... archived and frozen repositories",
                style="bold cyan",
            )
            console.print(
                "[dim]Repos marked as archived, unmaintained, or deprecated[/dim]"
            )
            console.print()
            display_results(items)

    except RuntimeError:
        # API errors already print to stderr
        sys.exit(1)
    except Exception as e:
        print(f"grave: error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_export(args: argparse.Namespace) -> None:
    """Export scan results in specified format."""
    from grave.api import build_search_query, check_gh_auth, search_repos
    from grave.presets import get_preset, list_presets

    try:
        # Branch: from database or from API search
        if args.from_db:
            # FROM DATABASE MODE
            from grave import db

            conn = db.init_db()
            items = db.list_repos(
                conn,
                language=args.language,
                stars=args.stars,
                preset=args.preset,
                since=args.since,
                limit=args.limit,
            )
            conn.close()

        else:
            # FROM API SEARCH MODE
            # Pre-flight check: verify gh CLI is authenticated
            if not check_gh_auth():
                sys.exit(1)

            # Branch: preset mode or custom search mode
            if args.preset:
                # PRESET MODE: Get the preset by name
                preset = get_preset(args.preset)
                if preset is None:
                    print(
                        f"grave: error: preset '{args.preset}' not found",
                        file=sys.stderr,
                    )
                    print("\nAvailable presets:", file=sys.stderr)
                    for p in list_presets():
                        print(f"  - {p.name}", file=sys.stderr)
                    sys.exit(1)

                # Build query with overrides from CLI flags
                if args.language or args.stars:
                    query = build_search_query(
                        keywords=preset.keywords if preset.keywords else None,
                        created_range=preset.created_range,
                        language=args.language if args.language else preset.language,
                        stars_range=args.stars if args.stars else preset.stars_range,
                    )
                else:
                    query = preset.build_query()

                # Execute search
                response = search_repos(query, limit=args.limit)
                items = response.get("items", [])

            else:
                # CUSTOM SEARCH MODE: Validate parameters
                if not any(
                    [
                        args.keyword,
                        args.created,
                        args.pushed,
                        args.language,
                        args.stars,
                        args.abandoned,
                        args.era,
                        args.dead_since,
                    ]
                ):
                    print(
                        "grave: error: at least one search parameter "
                        "is required (or use --preset)",
                        file=sys.stderr,
                    )
                    print(
                        "Usage: grave export [--preset <name>] [--keyword <word>] "
                        "[--format json|csv|ndjson]",
                        file=sys.stderr,
                    )
                    sys.exit(2)

                # Handle --era flag (takes precedence over --created)
                created_filter = args.created
                if args.era:
                    start_date, end_date = ERAS[args.era]
                    created_filter = f"{start_date}..{end_date}"

                # Handle pushed filters with precedence:
                # --dead-since > --abandoned > --pushed
                pushed_filter = args.pushed
                if args.dead_since:
                    pushed_filter = f"<{args.dead_since}-01-01"
                elif args.abandoned:
                    cutoff_year = date.today().year - args.abandoned
                    pushed_filter = f"<{cutoff_year}-01-01"

                # Build search query
                query = build_search_query(
                    keywords=args.keyword,
                    created_range=created_filter,
                    language=args.language,
                    stars_range=args.stars,
                    pushed=pushed_filter,
                )

                # Execute search with sort parameter
                response = search_repos(query, limit=args.limit, sort=args.sort)
                items = response.get("items", [])

        # Export in requested format
        if args.format == "json":
            # Pretty-printed JSON
            print(json.dumps(items, indent=2))
        elif args.format == "ndjson":
            # Newline-delimited JSON (one object per line)
            for item in items:
                print(json.dumps(item))
        elif args.format == "csv":
            # CSV format with standard fields
            if not items:
                return

            fieldnames = [
                "full_name",
                "description",
                "language",
                "stargazers_count",
                "created_at",
                "pushed_at",
                "html_url",
            ]
            writer = csv.DictWriter(
                sys.stdout, fieldnames=fieldnames, extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(items)

    except RuntimeError:
        # API errors already print to stderr
        sys.exit(1)
    except Exception as e:
        print(f"grave: error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="grave",
        description="GRAVE — Git Repository Abandonment & Vintage Explorer",
        epilog="Use 'grave <command> --help' for more information about a command.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="available commands")

    # grave init
    parser_init = subparsers.add_parser(
        "init",
        help="set up GRAVE for first use",
        description="Check prerequisites and set up GRAVE for digital archaeology.",
        epilog="""Example:
  grave init""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_init.set_defaults(func=cmd_init)

    # grave scan
    parser_scan = subparsers.add_parser(
        "scan",
        help="scan for repositories with preset or custom parameters",
        description="Scan for repositories using a preset or custom search parameters.",
        epilog="""Examples:
  grave scan --preset ancient
  grave scan --preset ancient --limit 5
  grave scan --preset dead-lang --language Perl
  grave scan --keyword "neural network" --created "2008-01-01..2012-12-31"
  grave scan --keyword fractal --abandoned 10
  grave scan --keyword web --created "2008-01-01..2010-12-31" --language Python
  grave scan --era y2k --keyword web
  grave scan --era early-github --language Ruby
  grave scan --dead-since 2015 --keyword python --limit 5""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_scan.add_argument(
        "--preset",
        help="name of preset to run",
    )
    parser_scan.add_argument(
        "--keyword",
        action="append",
        help="keyword to search for (can be used multiple times)",
    )
    parser_scan.add_argument(
        "--created",
        help="created date range (e.g., '2000-01-01..2010-12-31')",
    )
    parser_scan.add_argument(
        "--pushed",
        help="last push date range (e.g., '<2015-01-01')",
    )
    parser_scan.add_argument(
        "--abandoned",
        type=int,
        metavar="YEARS",
        help="find repos not pushed in N years (takes precedence over --pushed)",
    )
    parser_scan.add_argument(
        "--era",
        choices=list(ERAS.keys()),
        help="search by named era (takes precedence over --created)",
    )
    parser_scan.add_argument(
        "--dead-since",
        type=int,
        metavar="YEAR",
        help="find repos not pushed since YEAR (e.g., 2015 → pushed:<2015-01-01)",
    )
    parser_scan.add_argument(
        "--language",
        help="programming language filter",
    )
    parser_scan.add_argument(
        "--stars",
        help="stars filter (e.g., '>100', '10..50')",
    )
    parser_scan.add_argument(
        "--sort",
        choices=["stars", "forks", "updated"],
        default="stars",
        help="sort order (default: stars)",
    )
    parser_scan.add_argument(
        "--limit",
        type=int,
        default=30,
        help="maximum number of results to return (default: 30)",
    )
    parser_scan.add_argument(
        "--json",
        action="store_true",
        help="output raw JSON instead of formatted table",
    )
    parser_scan.set_defaults(func=cmd_scan)

    # grave dig <owner/repo>
    parser_dig = subparsers.add_parser(
        "dig",
        help="dig up detailed information about a repository",
        description="Dig up detailed information about a specific repository.",
        epilog="""Examples:
  grave dig torvalds/linux
  grave dig microsoft/MS-DOS
  grave dig torvalds/linux --json
  grave dig rails/rails --open""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_dig.add_argument(
        "repo",
        help="repository in 'owner/repo' format",
    )
    parser_dig.add_argument(
        "--json",
        action="store_true",
        help="output raw JSON instead of formatted panel",
    )
    parser_dig.add_argument(
        "--open",
        action="store_true",
        help="open repository in browser after displaying details",
    )
    parser_dig.set_defaults(func=cmd_dig)

    # grave list
    parser_list = subparsers.add_parser(
        "list",
        help="list all repositories from the database",
        description="List all repositories collected from previous scans.",
        epilog="""Examples:
  grave list
  grave list --language Python
  grave list --stars ">100"
  grave list --preset ancient
  grave list --since 2024-01-01 --limit 20""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_list.add_argument(
        "--language",
        help="filter by programming language",
    )
    parser_list.add_argument(
        "--stars",
        help="filter by stars (e.g., '>100', '<50', '100..200')",
    )
    parser_list.add_argument(
        "--preset",
        help="filter by preset name",
    )
    parser_list.add_argument(
        "--since",
        help="filter by first_seen date (ISO format, e.g., '2024-01-01')",
    )
    parser_list.add_argument(
        "--limit",
        type=int,
        default=50,
        help="maximum number of results (default: 50)",
    )
    parser_list.add_argument(
        "--json",
        action="store_true",
        help="output raw JSON instead of formatted table",
    )
    parser_list.set_defaults(func=cmd_list)

    # grave db
    parser_db = subparsers.add_parser(
        "db",
        help="database management commands",
        description="Manage the GRAVE database.",
        epilog="""Examples:
  grave db stats
  grave db path
  grave db clear --confirm
  grave db clear --scans --confirm
  grave db vacuum""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    db_subparsers = parser_db.add_subparsers(
        dest="db_command", help="database subcommands"
    )

    # grave db stats
    db_subparsers.add_parser(
        "stats",
        help="show database statistics",
        description="Show database statistics including counts and top languages.",
    )

    # grave db path
    db_subparsers.add_parser(
        "path",
        help="print database file path",
        description="Print the path to the database file.",
    )

    # grave db clear
    parser_db_clear = db_subparsers.add_parser(
        "clear",
        help="clear database data",
        description="Clear data from the database. Requires --confirm flag.",
    )
    parser_db_clear.add_argument(
        "--confirm",
        action="store_true",
        help="confirm the clear operation",
    )
    parser_db_clear.add_argument(
        "--scans",
        action="store_true",
        help="only clear scan history, keep repos",
    )

    # grave db vacuum
    db_subparsers.add_parser(
        "vacuum",
        help="compact the database",
        description="Run SQLite VACUUM to compact the database file.",
    )

    parser_db.set_defaults(func=cmd_db)

    # grave presets
    parser_presets = subparsers.add_parser(
        "presets",
        help="list all available preset search profiles",
        description="List all available preset search profiles.",
        epilog="""Examples:
  grave presets
  grave presets --category archaeology
  grave presets --category dead-languages""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_presets.add_argument(
        "--category",
        metavar="CATEGORY",
        help=(
            "filter presets by category "
            "(archaeology, dead-languages, eras, culture, science)"
        ),
    )
    parser_presets.set_defaults(func=cmd_presets)

    # grave export
    parser_export = subparsers.add_parser(
        "export",
        help="export scan results in specified format",
        description="Export scan results in JSON, CSV, or NDJSON format.",
        epilog="""Examples:
  grave export --preset ancient --limit 10 --format json
  grave export --keyword "fractal" --abandoned 5 --format ndjson
  grave export --preset cyber-relics --format csv
  grave export --from-db --language Python --format json
  grave export --from-db --preset ancient --format csv
  grave export --era y2k --keyword web --format json
  grave export --era early-github --language Ruby --format csv
  grave export --dead-since 2015 --keyword python --format ndjson""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_export.add_argument(
        "--preset",
        help="name of preset to run",
    )
    parser_export.add_argument(
        "--keyword",
        action="append",
        help="keyword to search for (can be used multiple times)",
    )
    parser_export.add_argument(
        "--created",
        help="created date range (e.g., '2000-01-01..2010-12-31')",
    )
    parser_export.add_argument(
        "--pushed",
        help="last push date range (e.g., '<2015-01-01')",
    )
    parser_export.add_argument(
        "--abandoned",
        type=int,
        metavar="YEARS",
        help="find repos not pushed in N years",
    )
    parser_export.add_argument(
        "--era",
        choices=list(ERAS.keys()),
        help="search by named era (takes precedence over --created)",
    )
    parser_export.add_argument(
        "--dead-since",
        type=int,
        metavar="YEAR",
        help="find repos not pushed since YEAR (e.g., 2015 → pushed:<2015-01-01)",
    )
    parser_export.add_argument(
        "--language",
        help="programming language filter",
    )
    parser_export.add_argument(
        "--stars",
        help="stars filter (e.g., '>100', '10..50')",
    )
    parser_export.add_argument(
        "--sort",
        choices=["stars", "forks", "updated"],
        default="stars",
        help="sort order (default: stars)",
    )
    parser_export.add_argument(
        "--limit",
        type=int,
        default=30,
        help="maximum number of results to return (default: 30)",
    )
    parser_export.add_argument(
        "--format",
        choices=["json", "csv", "ndjson"],
        default="json",
        help="output format (default: json)",
    )
    parser_export.add_argument(
        "--from-db",
        action="store_true",
        help="export from database instead of running a new search",
    )
    parser_export.add_argument(
        "--since",
        help="filter by first_seen date (ISO format, e.g., '2024-01-01') "
        "(only used with --from-db)",
    )
    parser_export.set_defaults(func=cmd_export)

    # grave random
    parser_random = subparsers.add_parser(
        "random",
        help="random archaeological dig — surprise yourself",
        description="Pick a random preset and discover something unexpected.",
        epilog="""Examples:
  grave random
  grave random --limit 5
  grave random --json""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_random.add_argument(
        "--limit",
        type=int,
        default=10,
        help="maximum number of results to return (default: 10)",
    )
    parser_random.add_argument(
        "--json",
        action="store_true",
        help="output raw JSON instead of formatted table",
    )
    parser_random.set_defaults(func=cmd_random)

    # grave rabbit-hole
    parser_rabbit_hole = subparsers.add_parser(
        "rabbit-hole",
        help="find repos similar to a given repository",
        description=(
            "Discover similar repos based on language, creation date, and topics."
        ),
        epilog="""Examples:
  grave rabbit-hole torvalds/linux
  grave rabbit-hole microsoft/MS-DOS --limit 20
  grave rabbit-hole rails/rails --json""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_rabbit_hole.add_argument(
        "repo",
        help="repository in 'owner/repo' format",
    )
    parser_rabbit_hole.add_argument(
        "--limit",
        type=int,
        default=10,
        help="maximum number of results to return (default: 10)",
    )
    parser_rabbit_hole.add_argument(
        "--json",
        action="store_true",
        help="output raw JSON instead of formatted table",
    )
    parser_rabbit_hole.set_defaults(func=cmd_rabbit_hole)

    # grave morgue
    parser_morgue = subparsers.add_parser(
        "morgue",
        help="find dead forks and repos with inactive owners",
        description=(
            "Search the morgue for dead forks, mirrors, and abandoned projects."
        ),
        epilog="""Examples:
  grave morgue
  grave morgue --limit 50
  grave morgue --json""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_morgue.add_argument(
        "--limit",
        type=int,
        default=20,
        help="maximum number of results to return (default: 20)",
    )
    parser_morgue.add_argument(
        "--json",
        action="store_true",
        help="output raw JSON instead of formatted table",
    )
    parser_morgue.set_defaults(func=cmd_morgue)

    # grave casket
    parser_casket = subparsers.add_parser(
        "casket",
        help="find archived and frozen repositories",
        description=(
            "Open the casket to find archived, unmaintained, and frozen repositories."
        ),
        epilog="""Examples:
  grave casket
  grave casket --language Python
  grave casket --limit 50 --json""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_casket.add_argument(
        "--language",
        help="filter by programming language",
    )
    parser_casket.add_argument(
        "--limit",
        type=int,
        default=20,
        help="maximum number of results to return (default: 20)",
    )
    parser_casket.add_argument(
        "--json",
        action="store_true",
        help="output raw JSON instead of formatted table",
    )
    parser_casket.set_defaults(func=cmd_casket)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
