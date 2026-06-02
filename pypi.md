# ⚰️ GRAVE — Git Repository Abandonment & Vintage Explorer

> Dig up dead, forgotten, and vintage GitHub repositories.

[![PyPI version](https://img.shields.io/pypi/v/grave-cli)](https://pypi.org/project/grave-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/grave-cli)](https://pypi.org/project/grave-cli/)
[![License: MIT](https://img.shields.io/pypi/l/grave-cli)](https://pypi.org/project/grave-cli/)

**GRAVE** is a command-line tool for *digital archaeology* — it hunts GitHub for the old, the obscure, and the abandoned.

GitHub is a graveyard of forgotten brilliance: repos with no stars that nobody ever saw, clever ideas from 2009 written in languages nobody uses anymore, projects abandoned the day someone lost their login and never came back. Somewhere in there is a gem worth resurrecting, modernizing, or mining for inspiration — and GRAVE is the shovel.

Point it at an era, a dead language, or a theme and it surfaces what time forgot. Then you open it, clone it, and decide what to do with it. **Stateless by design** — results stream to your terminal or to stdout; no database, nothing written to disk.

## Install

```bash
pipx install grave-cli      # recommended (isolated install)
# or
pip install grave-cli
```

> **Requires:** Python 3.13+ and the [GitHub CLI (`gh`)](https://cli.github.com), which handles all authentication — GRAVE never touches your credentials.

## Quick start

```bash
grave init                          # check prerequisites, sign in via gh
grave scan --preset ancient         # GitHub's oldest surviving repos
grave random                        # surprise me — a random preset
grave dig torvalds/linux --open     # deep-dive, then open in the browser
grave morgue                        # dead forks and abandoned mirrors
```

## Ways to dig

- **27 curated presets** across 5 themes — archaeology, dead languages, eras, internet culture, and weird science. Browse them with `grave presets`.
- **Era search** — named time windows: `--era y2k`, `dotcom`, `web2.0`, `early-github`, `pre-mobile`.
- **Abandonment filters** — `--abandoned 10` (untouched 10+ years), `--dead-since 2015`.
- **Dead-language hunts** — Perl, Pascal, COBOL, Tcl, Smalltalk, ActionScript, and other survivors.
- **Thematic lenses** — `grave morgue` (dead forks, mirrors, 404s) and `grave casket` (archived / deprecated / read-only).
- **Serendipity** — `grave random` for a blind dig, `grave rabbit-hole <owner/repo>` to find more like something you just unearthed.
- **Custom queries** — mix `--keyword`, `--created`, `--language`, `--stars`, and `--pushed` however you like.

Every result is a rich, clickable table; `grave dig` opens a full panel for a single repo.

## Commands

| Command | Description |
|---|---|
| `grave init` | First-time setup and prerequisite checks |
| `grave scan` | Search with a preset or custom parameters |
| `grave dig <owner/repo>` | Deep-dive into a specific repository |
| `grave random` | Random preset — the archaeology slot machine |
| `grave rabbit-hole <owner/repo>` | Find repositories similar to one you like |
| `grave morgue` | Dead forks, mirrors, and abandoned projects |
| `grave casket` | Archived, deprecated, and read-only repositories |
| `grave export` | Run a live search and emit JSON / CSV / NDJSON to stdout |
| `grave presets` | List all 27 curated presets |

## Save a dig

GRAVE keeps no database on purpose — if you want to keep a find, pipe it:

```bash
grave export --preset dead-lang-cobol --format ndjson > cobol-relics.ndjson
grave export --keyword fractal --abandoned 10 --format csv > fractals.csv
```

## Links

- **Source:** [github.com/ul0gic/grave](https://github.com/ul0gic/grave)
- **Issues:** [github.com/ul0gic/grave/issues](https://github.com/ul0gic/grave/issues)
- **License:** MIT
