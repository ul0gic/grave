"""Argument parsing and command dispatch for grave.

Builds the argparse tree, wires each subcommand to its handler in
:mod:`grave.commands`, and dispatches. The dispatch layer is the single place
that renders typed errors: :class:`~grave.errors.UsageError` (exit 2) and
:class:`~grave.integrations.github.GhError` (exit 1).
"""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import version

from grave.commands.dig import cmd_dig
from grave.commands.export import cmd_export
from grave.commands.init import cmd_init
from grave.commands.presets import cmd_presets
from grave.commands.rabbit_hole import cmd_rabbit_hole
from grave.commands.random import cmd_random
from grave.commands.scan import cmd_scan
from grave.commands.themed import cmd_themed
from grave.config.eras import ERAS


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
        version=f"%(prog)s {version('grave-cli')}",
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
        help=("filter presets by category (archaeology, culture, dead-languages, eras, science)"),
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
        description=("Discover similar repos based on language, creation date, and topics."),
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
        description=("Search the morgue for dead forks, mirrors, and abandoned projects."),
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
    parser_morgue.set_defaults(func=cmd_themed, lens="morgue")

    # grave casket
    parser_casket = subparsers.add_parser(
        "casket",
        help="find archived and frozen repositories",
        description=("Open the casket to find archived, unmaintained, and frozen repositories."),
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
    parser_casket.set_defaults(func=cmd_themed, lens="casket")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    from grave.errors import UsageError
    from grave.integrations.github import GhError

    try:
        args.func(args)
    except UsageError as e:
        print(f"grave: error: {e.message}", file=sys.stderr)
        for line in e.hints:
            print(line, file=sys.stderr)
        sys.exit(2)
    except GhError as e:
        print(f"grave: error: {e}", file=sys.stderr)
        sys.exit(1)
