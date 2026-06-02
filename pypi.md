# GRAVE — Git Repository Abandonment & Vintage Explorer

Dig up dead, forgotten, and vintage GitHub repositories.

**GRAVE** is a command-line tool for digital archaeology. It searches GitHub for old, weird, abandoned, and forgotten repositories using 27 curated preset profiles and custom queries. Stateless by design — results stream to your terminal or to stdout via `export`, with no database and nothing written to disk.

## Install

```bash
pipx install grave-cli
```

Or with pip:

```bash
pip install grave-cli
```

> **Requires:** Python 3.13+ and [gh CLI](https://cli.github.com) (handles all GitHub authentication)

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
- **Rich terminal UI** with clickable hyperlinks, colored tables, and formatted panels
- **Export** to JSON, CSV, or NDJSON — live results streamed to stdout
- **Stateless** — no database, no `~/.local/share/grave`, nothing written to disk

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
| `grave export` | Run a live search and emit results as JSON, CSV, or NDJSON to stdout |
| `grave presets` | List all 27 search presets |

## Links

- **GitHub:** [github.com/ul0gic/grave](https://github.com/ul0gic/grave)
- **Issues:** [github.com/ul0gic/grave/issues](https://github.com/ul0gic/grave/issues)
- **License:** MIT
