# Changelog

All notable changes to **asoscope** are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-08-31

### Added
- `search`: multi-storefront app search with genre, price, minimum-rating
  filters and relevance / rating / rating-count / name ordering.
- `lookup`: full app metadata by numeric track id or bundle id.
- `reviews`: public customer-review fetching (recent / helpful) with an
  optional `--stats` rating-distribution report.
- `charts`: public top-free / top-paid / top-grossing / new-release
  charts, per country and per genre.
- `compare`: side-by-side comparison of two or more apps, accepting a
  mix of numeric ids and bundle ids.
- `watch`: local-first watchlist with append-only snapshots and a `diff`
  view for version / price / rating / size changes.
- Output formats: aligned terminal table (CJK-aware), JSON, CSV and
  Markdown; `--output` writes any format to a file.
- Zero third-party runtime dependencies — Python 3.8+ standard library
  only; cross-platform on Windows, macOS and Linux.
- On-disk TTL response cache, bounded retries with exponential backoff.
- Full `unittest` suite using captured Apple response fixtures (no
  network required to run tests).
