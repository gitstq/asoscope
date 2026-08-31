<div align="center">

# 🔭 asoscope — Zero-Dependency App Store Intelligence CLI

**Search, inspect, compare and watch App Stores worldwide straight from your terminal — public Apple endpoints only, no login, no API key, no IPA downloads.**

[![Python](https://img.shields.io/badge/python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](../LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-success.svg)](#-design-philosophy--roadmap)
[![Platforms](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#-requirements)
[![Tests](https://img.shields.io/badge/tests-54%20passed-success.svg)](#-running-the-tests)

**🌐 Languages: [简体中文](../README.md) · [繁體中文](README.zh-TW.md) · English**

</div>

---

## 🎉 Introduction

**asoscope** is a local-first command-line workbench for App Store intelligence, built for indie developers, ASO (App Store Optimization) practitioners, product managers, competitive analysts and automation pipelines. It wraps Apple's official **iTunes Search API** and the **public RSS chart/review feeds** behind a small, composable set of terminal commands: search apps across 175 storefronts, read full metadata, harvest customer reviews and rating distributions, browse category charts, compare competitors side by side, and watch a local list of apps with automatic snapshots of version, price and rating changes.

### 😮‍💨 The problems it solves

- 🧭 **Too many browser tabs, nothing scriptable.** The App Store website is painful for batch lookups and cannot be piped into automation. asoscope returns structured results in one command, with table / JSON / CSV / Markdown output and file export.
- 🔐 **Existing tools are risky.** Some tools require an Apple ID sign-in, call private endpoints, or download IPA binaries — exposing accounts and creating legal risk. asoscope only touches Apple's **public, keyless, read-only endpoints: no authentication, no private APIs, no IPA downloads**.
- 🧱 **Heavy runtimes.** Many CLIs drag in a deep dependency tree ("dependency hell" on install). asoscope uses **nothing but the Python 3.8+ standard library — zero third-party runtime dependencies** — and behaves identically on Windows, macOS and Linux.
- 📊 **Manual competitive tracking.** A built-in local watchlist with snapshot diffs makes version releases, price moves and rating shifts obvious. Data stays on your machine; there is no telemetry, ever.

### 💡 Inspiration and differentiation

The product idea was inspired by [majd/ipatool](https://github.com/majd/ipatool), a trending GitHub project (written in Go) for searching and downloading App Store packages from the terminal — it proved the demand for "App Store operations on the command line". asoscope **copies none of its code** and deliberately takes a safer, more general path:

| Dimension | Classic IPA tooling | **asoscope (this project)** |
| --- | --- | --- |
| Endpoints | Apple ID auth + private endpoints | ✅ Public, keyless, read-only only |
| Compliance risk | Account / distribution risk | ✅ No login, no IPA download |
| Core capability | Downloading binaries | ✅ Metadata intelligence: search / lookup / reviews / charts / compare / watch |
| Runtime | Platform-specific binary | ✅ Python standard library, zero deps, cross-platform |
| Output | Downloaded files | ✅ Table / JSON / CSV / Markdown, automation-first |

> ⚖️ asoscope uses public Apple data endpoints exclusively and is intended for lawful market research and developer analysis. Please comply with local laws and Apple's terms of service.

---

## ✨ Highlights

- 🌍 **Worldwide multi-storefront search** — any ISO 3166-1 alpha-2 region (`us`, `jp`, `gb`, `cn`, …), iPhone/iPad entity, genre and free/paid filters, minimum-rating filter, and relevance / rating / rating-count / name ordering.
- 🪪 **Two lookup modes** — `lookup` accepts either a numeric track ID or a bundle ID (e.g. `com.duolingo.DuolingoMobile`) and returns 40+ normalized metadata fields.
- 💬 **Public review harvesting** — page through customer reviews sorted by most-recent or most-helpful; `--stats` collapses a page into a 1–5 star distribution and average.
- 🏆 **Public charts** — top-free, top-paid, top-grossing and new-release charts with country, genre and limit parameters.
- ⚖️ **Side-by-side comparison** — `compare` accepts a mixed list of track IDs and bundle IDs and renders one comparison table.
- 👀 **Local watchlist + snapshot diffs** — `watch` tracks apps locally; repeated snapshots detect changes in version, price, average rating, rating count, binary size and release date. **Everything stays on your machine.**
- 🧮 **Four export formats** — aligned terminal tables (**CJK/full-width-width aware, so Japanese and Chinese names never misalign**), JSON, CSV and Markdown; write anywhere with `-o` for Excel, BI or CI pipelines.
- 🧰 **Zero third-party runtime dependencies** — Python stdlib only, with a TTL disk cache, exponential-backoff retries and deterministic process exit codes.
- 🧪 **Fully offline test suite** — 54 unit tests run against real, captured and trimmed endpoint fixtures; no network required to test.

---

## 🚀 Quick Start

### 📌 Requirements

| Item | Requirement |
| --- | --- |
| Python | **3.8 or newer** (verified on 3.8 / 3.9 / 3.10 / 3.11 / 3.12) |
| OS | Windows 10+, macOS 11+, any mainstream Linux distribution |
| Network | Only needs to reach `itunes.apple.com` (Apple's public endpoints) |
| Account / key | ❌ No Apple ID, no API key |
| Third-party dependencies | ❌ Zero |

Check your Python:

```bash
python3 --version   # on Windows this is usually: python --version
```

### 📦 Installation

**Option 1 — pip (recommended)**

```bash
pip install asoscope-cli
```

**Option 2 — pipx isolated install (best practice for CLIs)**

```bash
pipx install asoscope-cli
```

**Option 3 — run from source without installing**

```bash
git clone https://github.com/gitstq/asoscope.git
cd asoscope
python3 -m asoscope --version
```

Verify the install:

```bash
asoscope --version     # prints asoscope 1.0.0
asoscope --help        # show all commands
```

### ⚡ One-minute tour (copy-paste ready)

```bash
# 1. Search free US habit trackers, best-rated first, top 5
asoscope search "habit tracker" --price free --sort rating -n 5

# 2. Full metadata by bundle ID as JSON
asoscope lookup --bundle com.duolingo.DuolingoMobile -f json

# 3. Top-10 free games on the Japanese storefront, Markdown output
asoscope -c jp charts top-free --genre games -n 10 -f md

# 4. Rating distribution from the most-recent review page
asoscope reviews 570060128 --stats

# 5. Watch a competitor: add, snapshot, diff
asoscope watch add 570060128
asoscope watch snapshot
asoscope watch diff
```

---

## 📖 In-Depth Guide

### 🧭 Command map

```text
asoscope [global options] <command> [command options]

Commands:
  search    Search apps
  lookup    Full metadata for a single app
  reviews   Public customer reviews / rating distribution
  charts    Public charts (top-free / top-paid / top-grossing / new)
  compare   Compare two or more apps side by side
  watch     Local watchlist: add / rm / ls / snapshot / diff
  genres    List supported genre aliases and numeric IDs
```

### 🎛️ Global options (work before *or* after the subcommand)

| Option | Description | Default |
| --- | --- | --- |
| `-c, --country` | Storefront, two-letter ISO region code | `us` |
| `-f, --format` | Output format: `table` / `json` / `csv` / `md` | `table` |
| `-o, --output` | Write to a file instead of stdout | — |
| `--timeout` | Per-request timeout in seconds | `15` |
| `--no-cache` | Bypass the local TTL cache | off |
| `--data-dir` | Override the directory holding `watchlist.json` | OS default |

> 💡 Both positions are equivalent: `asoscope -f json search notion` and `asoscope search notion -f json` produce identical output.

### 1) 🔍 search

```bash
asoscope search <term> [options]
```

| Option | Description |
| --- | --- |
| `-n, --limit` | Result count, 1–200 (default 20) |
| `--device` | `iphone` (default) or `ipad` |
| `--genre` | Genre alias (`games`, `productivity`, …) or a numeric Apple genre ID |
| `--price` | `free` / `paid` / `all` |
| `--min-rating` | Keep apps with average rating at or above this value |
| `--sort` | `relevance` (default) / `rating` / `ratings` / `name` |

Example:

```bash
# Free US productivity note apps rated 4.5+, by rating count, exported to CSV
asoscope search "notes" --genre productivity --price free \
  --min-rating 4.5 --sort ratings -f csv -o notes.csv
```

### 2) 🪪 lookup — full metadata

```bash
asoscope lookup --id 570060128                          # by track ID
asoscope lookup --bundle com.duolingo.DuolingoMobile   # by bundle ID
```

Table mode lists every field: developer, seller, version, price and currency, overall/current-version ratings, genres, content rating, binary size (MB), minimum OS, languages, release/current-version dates, release notes, store URL, icon URL and description. JSON mode emits the full normalized object for programmatic use.

### 3) 💬 reviews — customer voice

```bash
asoscope reviews <track_id> [--page 1] [--sort recent|helpful] [--stats]
```

```bash
# Page 2 of the most-helpful reviews as JSON
asoscope reviews 570060128 --page 2 --sort helpful -f json

# Only the rating distribution (count, page average, 1–5 star buckets)
asoscope reviews 570060128 --stats
```

### 4) 🏆 charts

```bash
asoscope charts <top-free|top-paid|top-grossing|new> [--genre GENRE] [-n N]
```

```bash
# Top-20 paid finance apps on the Hong Kong storefront
asoscope -c hk charts top-paid --genre finance -n 20
```

### 5) ⚖️ compare — competitor matrix

Mix track IDs and bundle IDs; at least two targets:

```bash
asoscope compare 570060128 com.mojang.minecraftpe -f md
```

### 6) 👀 watch — local watchlist and change monitoring

The watchlist is a human-readable JSON file (`watchlist.json`) that lives only on your machine and is never uploaded.

```bash
asoscope watch add <track_id or bundle_id>   # ➕ Add (the first lookup is stored as the baseline snapshot)
asoscope watch ls                            # 📋 List every watched app
asoscope watch snapshot                      # 📸 Take a fresh snapshot of every watched app
asoscope watch snapshot --id 570060128       # 📸 Snapshot a single app
asoscope watch diff                          # 🔍 Diff the latest two snapshots
asoscope watch rm <track_id>                 # 🗑️ Remove an app
```

A typical setup runs `snapshot` + `diff` daily via cron (Linux/macOS) or Task Scheduler (Windows) for hands-off competitor monitoring. The diff watches **version, price, formatted price, average rating, rating count, binary size and current-version release date**.

### 🗂️ Data and cache directories (cross-platform)

| Platform | Data directory | Cache directory |
| --- | --- | --- |
| Windows | `%LOCALAPPDATA%\asoscope` | `%LOCALAPPDATA%\asoscope\cache` |
| macOS | `~/Library/Application Support/asoscope` | `~/Library/Caches/asoscope` |
| Linux | `$XDG_DATA_HOME/asoscope` or `~/.local/share/asoscope` | `$XDG_CACHE_HOME/asoscope` or `~/.cache/asoscope` |

Override with the `ASOSCOPE_DATA_DIR` / `ASOSCOPE_CACHE_DIR` environment variables or the `--data-dir` option.

### 🧑‍💻 Embedding asoscope as a library

asoscope is also a clean library you can embed:

```python
from asoscope.api import AppStoreClient
from asoscope.http import HttpClient, DiskCache

client = AppStoreClient(HttpClient(cache=DiskCache("./.cache")))
apps = client.search("habit tracker", country="us", price="free", sort="rating")
for app in apps[:5]:
    print(app.track_id, app.track_name, app.average_rating, app.formatted_price)

app = client.lookup(bundle_id="com.duolingo.DuolingoMobile")
reviews = client.reviews(app.track_id, country="us", sort="helpful")
```

### 🚦 Exit codes (for scripting)

| Code | Meaning |
| --- | --- |
| 0 | Success |
| 1 | Generic error |
| 2 | Usage error (e.g. invalid country code) |
| 3 | Network / endpoint error (including exhausted retries) |
| 4 | Target app not found |
| 5 | Local watchlist read/write error |

### 🖼️ Screenshots / demo recordings

> 📸 Placeholder for screenshots and terminal recordings, recommended under `docs/demo/`:
>
> - `docs/demo/search-demo.svg` — search and multi-format export
> - `docs/demo/watch-diff.gif` — watchlist snapshot and diff workflow
>
> Demo assets are warmly welcomed via pull request!

### 🧯 FAQ

**Do I need an Apple ID or API key?**
No. asoscope only calls Apple's public, keyless, read-only endpoints.

**Why doesn't search order exactly match the App Store on my phone?**
The public Search API relevance order differs from a personalized, signed-in storefront — that is an Apple-side behavior. Use `--sort rating|ratings` for deterministic ordering.

**How many reviews can I fetch at once?**
The public review RSS returns up to ~50 reviews per page; page further with `--page`. Apple does not expose a full-review export.

**What does exit code 3 (network error) mean?**
Check connectivity to `itunes.apple.com` and increase `--timeout` if needed; bounded exponential-backoff retries are already built in.

---

## 💡 Design Philosophy & Roadmap

### 🧱 Why this stack

- **Python stdlib, zero third-party deps.** `urllib` handles HTTP; `json`, `csv`, `dataclasses`, `argparse` and `unittest` cover everything else. This minimizes install cost, maximizes cross-platform consistency and removes supply-chain risk.
- **Layered architecture.** `http` (transport / retries / cache) → `models` (normalizing three Apple payload shapes) → `api` (endpoints + business filters) → `store` (local state) → `render` (serialization) → `cli` (arguments + orchestration). Each layer is independently testable and replaceable.
- **Testability first.** The transport is decoupled through an injectable opener; tests run fully offline against real captured fixtures — deterministic and fast.
- **Local-first, zero telemetry.** Watchlist and cache are local, atomically written JSON files; the program contains no reporting code whatsoever.

### 🗺️ Roadmap

- [ ] v1.1: review keyword aggregation and automatic multi-page review export
- [ ] v1.2: Markdown `watch diff` reports with email / webhook notifications
- [ ] v1.3: chart-history sampling and rank-movement trends
- [ ] v1.4: Mac App Store (macOS software) media support
- [ ] v1.5: optional TOML config and batch-query job lists

### 🙋 How to contribute

Genre aliases, additional language docs, demo assets, edge-case fixtures, table-rendering polish — all welcome. See [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## 📦 Packaging & Deployment

asoscope is a **tool/library project** (a cross-platform Python package with no native binaries), so it ships as a universal wheel instead of per-OS executables: one `pip install` works on every platform.

### 🔨 Building the wheel from source

```bash
# macOS / Linux (runs the test suite first)
bash scripts/build.sh

# Windows PowerShell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1

# Or via the Makefile
make build
```

The artifact lands at `dist/asoscope_cli-<version>-py3-none-any.whl` — a universal wheel (`py3-none-any`) that installs on all three platforms:

```bash
pip install dist/asoscope_cli-1.0.0-py3-none-any.whl
```

### ✅ Running the tests

```bash
make test
# equivalent to
python3 -m unittest discover -s tests -v
```

### 🚢 Servers / CI deployment

```bash
pip install asoscope-cli
# Emit a JSON artifact directly in CI
asoscope -c us charts top-free -n 50 -f json -o topfree.json
```

Compatibility: Python 3.8+ on Windows, macOS and Linux; no compilation step, no native dependencies.

---

## 🤝 Contributing

Issues, pull requests and documentation improvements are welcome. Please read [CONTRIBUTING.md](../CONTRIBUTING.md) first; the key rules:

1. **Branches & commits:** use `feat/xxx`, `fix/xxx` branches; Angular Conventional Commits (`feat:` / `fix:` / `docs:` / `refactor:` / `test:` / `chore:`).
2. **Zero-dependency red line:** any new runtime third-party dependency needs a prior issue and strong justification; if the stdlib can do it, the stdlib it is.
3. **Offline tests:** add trimmed fixtures for new endpoints; tests must never require the network.
4. **Compatibility:** stay on Python 3.8 syntax/stdlib and respect cross-platform path differences.
5. One logical change per PR; update `CHANGELOG.md` accordingly.

---

## 📄 License

Released under the **[MIT License](../LICENSE)** — free to use, modify, distribute and commercialize, as long as the copyright and permission notice are retained.

---

<div align="center">

If asoscope saved you a few dozen browser tabs, a ⭐ is much appreciated!

**🌐 [简体中文](../README.md) · [繁體中文](README.zh-TW.md) · English**

</div>
