# GRAVE — Git Repository Abandonment & Vintage Explorer

Dig up dead, forgotten, and vintage GitHub repositories.

**GRAVE** is a command-line tool for digital archaeology. It searches GitHub for old, weird, abandoned, and forgotten repositories using 27 curated preset profiles and custom queries. Every result is persisted locally in SQLite so you can build your own collection of internet history.

## Install

```bash
pipx install grave-cli
```

Or with pip:

```bash
pip install grave-cli
```

> **Requires:** Python 3.10+ and [gh CLI](https://cli.github.com) (handles all GitHub authentication)

## Quick Start

```bash
# First-time setup (checks prerequisites)
grave init

# Start digging
grave scan --preset ancient
grave random
grave dig torvalds/linux --open
```

## What It Does

- **27 curated presets** across 5 categories (archaeology, dead languages, eras, culture, science)
- **Era-based search** with named time windows (Y2K, dotcom bubble, Web 2.0, early GitHub)
- **Smart abandonment filters** (`--abandoned`, `--dead-since`)
- **Discovery commands** like `grave random` and `grave rabbit-hole`
- **Thematic exploration** with `grave morgue` (dead forks) and `grave casket` (archived repos)
- **SQLite persistence** with automatic deduplication and scan history
- **Rich terminal UI** with clickable hyperlinks, colored tables, and formatted panels
- **Export** to JSON, CSV, or NDJSON

## Commands

| Command | Description |
|---|---|
| `grave init` | First-time setup and prerequisite checks |
| `grave scan` | Search with presets or custom parameters |
| `grave dig <owner/repo>` | Deep-dive into a specific repository |
| `grave random` | Random preset slot machine |
| `grave rabbit-hole <owner/repo>` | Find similar repos |
| `grave morgue` | Search for dead forks |
| `grave casket` | Find archived repositories |
| `grave list` | Browse your collected repos |
| `grave export` | Export as JSON, CSV, or NDJSON |
| `grave presets` | List all 27 search presets |

## Links

- **GitHub:** [github.com/ul0gic/grave](https://github.com/ul0gic/grave)
- **Issues:** [github.com/ul0gic/grave/issues](https://github.com/ul0gic/grave/issues)
- **License:** MIT
