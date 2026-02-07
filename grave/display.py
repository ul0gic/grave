"""Rich terminal display formatting for grave output.

This module handles all terminal output formatting using the rich library,
including tables for search results and detailed panels for repository info.
"""

from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def display_results(repos: list[dict]) -> None:
    """Display search results as a rich table.

    Args:
        repos: List of repository data dictionaries from GitHub API
    """
    # Handle empty results
    if not repos:
        console.print("\n[yellow]No repositories found.[/yellow]\n")
        console.print("Try:", style="bold")
        console.print("  - Broadening your date range", style="dim")
        console.print("  - Using fewer keywords", style="dim")
        console.print(
            "  - Checking a different preset (run 'grave presets' to see options)",
            style="dim",
        )
        console.print()
        return

    # Show result count
    console.print(f"\nFound {len(repos)} repositories\n")

    # Create table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Repo", style="bold", no_wrap=True)
    table.add_column("Description", max_width=60)
    table.add_column("Language")
    table.add_column("Stars", justify="right")
    table.add_column("Created")
    table.add_column("Last Push")

    # Add rows
    for repo in repos:
        full_name = repo.get("full_name", "N/A")
        html_url = repo.get("html_url", "")

        # Make repo name clickable if URL is available
        repo_link = (
            f"[link={html_url}]{full_name}[/link]" if html_url else full_name
        )

        description = repo.get("description", "")
        if description and len(description) > 60:
            description = description[:57] + "..."
        if not description:
            description = "[dim]No description[/dim]"

        language = repo.get("language", "")
        if not language:
            language = "[dim]None[/dim]"

        stars = repo.get("stargazers_count", 0)
        stars_display = f"⭐ {stars:,}"

        # Format dates to YYYY-MM-DD
        created_at = repo.get("created_at", "")
        created_display = _format_date(created_at) if created_at else "N/A"

        pushed_at = repo.get("pushed_at", "")
        pushed_display = _format_date(pushed_at) if pushed_at else "N/A"

        table.add_row(
            repo_link,
            description,
            language,
            stars_display,
            created_display,
            pushed_display,
        )

    console.print(table)


def _format_date(iso_date: str) -> str:
    """Format ISO 8601 date string to YYYY-MM-DD.

    Args:
        iso_date: ISO 8601 formatted date string (e.g., '2010-03-15T12:00:00Z')

    Returns:
        Date formatted as YYYY-MM-DD
    """
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        return iso_date


def display_repo_detail(repo: dict) -> None:
    """Display detailed repository information in a rich panel.

    Args:
        repo: Repository data dictionary from GitHub API
    """
    # Header with repo name and description
    full_name = repo.get("full_name", "N/A")
    description = repo.get("description", "No description available")

    header = Text()
    header.append(full_name, style="bold cyan")
    if description:
        header.append("\n")
        header.append(description, style="dim")

    # Build stats table
    stats_table = Table.grid(padding=(0, 2))
    stats_table.add_column(style="bold")
    stats_table.add_column()

    # Stats
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    watchers = repo.get("watchers_count", 0)
    open_issues = repo.get("open_issues_count", 0)

    stats_table.add_row("⭐ Stars:", f"{stars:,}")
    stats_table.add_row("🔱 Forks:", f"{forks:,}")
    stats_table.add_row("👀 Watchers:", f"{watchers:,}")
    stats_table.add_row("🐛 Open Issues:", f"{open_issues:,}")

    # Language
    language = repo.get("language", "Not specified")
    stats_table.add_row("💻 Language:", language)

    # Dates
    created_at = repo.get("created_at", "")
    created_display = _format_date(created_at) if created_at else "N/A"
    pushed_at = repo.get("pushed_at", "")
    pushed_display = _format_date(pushed_at) if pushed_at else "N/A"
    updated_at = repo.get("updated_at", "")
    updated_display = _format_date(updated_at) if updated_at else "N/A"

    stats_table.add_row("📅 Created:", created_display)
    stats_table.add_row("📤 Last Push:", pushed_display)
    stats_table.add_row("🔄 Last Update:", updated_display)

    # Topics
    topics = repo.get("topics", [])
    if topics:
        topics_str = ", ".join(topics)
        stats_table.add_row("🏷️  Topics:", topics_str)

    # URL
    html_url = repo.get("html_url", "")
    url_display = f"[link={html_url}]{html_url}[/link]" if html_url else "N/A"
    stats_table.add_row("🔗 URL:", url_display)

    # Create panel
    panel = Panel(
        stats_table,
        title=header,
        border_style="cyan",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)
    console.print()


def display_presets(presets: list, category: str | None = None) -> None:
    """Display list of available presets grouped by category.

    Args:
        presets: List of Preset objects
        category: Optional category filter (only used for title display)
    """
    # Group presets by category
    from collections import defaultdict

    by_category = defaultdict(list)
    for preset in presets:
        by_category[preset.category].append(preset)

    # Display header
    if category:
        cat_title = category.replace("-", " ").title()
        title = f"[bold cyan]Search Presets - {cat_title}[/bold cyan]"
    else:
        title = "[bold cyan]Available Search Presets[/bold cyan]"

    console.print(f"\n{title}\n")

    # Display each category section
    for cat in sorted(by_category.keys()):
        cat_presets = by_category[cat]
        cat_title = cat.replace("-", " ").title()
        count = len(cat_presets)

        console.print(f"\n[bold yellow]{cat_title}[/bold yellow] ({count} presets)")

        table = Table(show_header=True, header_style="bold cyan", box=None)
        table.add_column("Name", style="bold green")
        table.add_column("Description")
        table.add_column("Keywords")
        table.add_column("Date Range")
        table.add_column("Language")

        for preset in cat_presets:
            name = preset.name
            description = preset.description
            keywords = (
                ", ".join(preset.keywords) if preset.keywords else "[dim]None[/dim]"
            )
            date_range = (
                preset.created_range if preset.created_range else "[dim]Any[/dim]"
            )
            language = preset.language if preset.language else "[dim]Any[/dim]"

            table.add_row(name, description, keywords, date_range, language)

        console.print(table)

    console.print(
        "\nUse [bold]grave scan --preset <name>[/bold] to run a preset search.\n"
    )
