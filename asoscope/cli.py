"""asoscope command line interface."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from typing import Any, Dict, List, Optional, Sequence

from . import __version__
from .api import CHART_FEEDS, GENRES, AppStoreClient, normalize_country
from .errors import AScopeError
from .http import DiskCache, HttpClient
from .render import render
from .store import WatchStore, default_cache_dir, default_data_dir
from .text import truncate

# Unified, stable column orders per command.
APP_COLUMNS = [
    ("track_id", "ID"),
    ("track_name", "Name"),
    ("developer", "Developer"),
    ("version", "Version"),
    ("formatted_price", "Price"),
    ("average_rating", "Rating"),
    ("rating_count", "Ratings"),
    ("primary_genre", "Genre"),
    ("country", "Store"),
    ("url", "URL"),
]
REVIEW_COLUMNS = [
    ("review_id", "Review ID"),
    ("author", "Author"),
    ("rating", "Stars"),
    ("version", "Version"),
    ("title", "Title"),
    ("updated", "Updated"),
    ("content", "Content"),
]
CHART_COLUMNS = [
    ("rank", "#"),
    ("track_id", "ID"),
    ("track_name", "Name"),
    ("developer", "Developer"),
    ("category", "Category"),
    ("price_label", "Price"),
    ("url", "URL"),
]
WATCH_COLUMNS = [
    ("track_id", "ID"),
    ("track_name", "Name"),
    ("bundle_id", "Bundle ID"),
    ("country", "Store"),
    ("snapshot_count", "Snapshots"),
    ("added_at", "Added At"),
]
DIFF_COLUMNS = [("field", "Field"), ("old", "Previous"), ("new", "Latest")]


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    """Register options that work both before and after the subcommand.

    Defaults use ``SUPPRESS`` so a sub-parser never resets a value already
    parsed from the global position (e.g. ``asoscope -f json search x``).
    Baseline defaults are installed once via ``set_defaults``.
    """
    parser.add_argument("-c", "--country", default=argparse.SUPPRESS,
                        help="App Store storefront, ISO 3166-1 alpha-2 (default: us)")
    parser.add_argument("-f", "--format", default=argparse.SUPPRESS,
                        choices=["table", "json", "csv", "md"],
                        help="output format (default: table)")
    parser.add_argument("-o", "--output", default=argparse.SUPPRESS,
                        help="write result to a file instead of stdout")
    parser.add_argument("--timeout", type=float, default=argparse.SUPPRESS,
                        help="per-request timeout in seconds (default: 15)")
    parser.add_argument("--no-cache", action="store_true", default=argparse.SUPPRESS,
                        help="bypass the on-disk response cache")
    parser.add_argument("--data-dir", default=argparse.SUPPRESS,
                        help="override the directory holding watchlist.json")


def build_parser() -> argparse.ArgumentParser:
    def common_parser() -> argparse.ArgumentParser:
        # A fresh instance per consumer: argparse shares parent actions by
        # reference, so reusing one instance would let the main parser's
        # set_defaults baseline leak into every sub-parser.
        parent = argparse.ArgumentParser(add_help=False)
        _add_common_options(parent)
        return parent

    parser = argparse.ArgumentParser(
        prog="asoscope",
        parents=[common_parser()],
        description="Zero-dependency App Store intelligence CLI "
        "(public iTunes Search API + public RSS; no login, no IPA download).",
        epilog="Run 'asoscope <command> --help' for command-specific options.",
    )
    parser.set_defaults(country="us", format="table", output=None, timeout=15.0,
                        no_cache=False, data_dir=None)
    parser.add_argument("--version", action="version", version=f"asoscope {__version__}")

    sub = parser.add_subparsers(dest="command", metavar="<command>")

    p_search = sub.add_parser("search", parents=[common_parser()],
                              help="search apps on a storefront")
    p_search.add_argument("term", help="search keywords, e.g. 'habit tracker'")
    p_search.add_argument("-n", "--limit", type=int, default=20, help="max results (1-200)")
    p_search.add_argument("--device", choices=["iphone", "ipad"], default="iphone")
    p_search.add_argument("--genre", help="genre alias (e.g. games) or numeric genre id")
    p_search.add_argument("--price", choices=["free", "paid", "all"], help="price filter")
    p_search.add_argument("--min-rating", type=float, help="keep apps rated at/above this")
    p_search.add_argument("--sort", choices=["relevance", "rating", "ratings", "name"],
                          default="relevance", help="client-side ordering")

    p_lookup = sub.add_parser("lookup", parents=[common_parser()], help="full metadata for one app")
    src = p_lookup.add_mutually_exclusive_group(required=True)
    src.add_argument("--id", dest="track_id", type=int, help="numeric track id")
    src.add_argument("--bundle", dest="bundle_id", help="bundle identifier, e.g. com.app.example")

    p_reviews = sub.add_parser("reviews", parents=[common_parser()], help="fetch public customer reviews")
    p_reviews.add_argument("track_id", type=int, help="numeric track id")
    p_reviews.add_argument("--page", type=int, default=1, help="RSS page number (from 1)")
    p_reviews.add_argument("--sort", choices=["recent", "helpful"], default="recent")
    p_reviews.add_argument("--stats", action="store_true",
                           help="report rating distribution instead of raw reviews")

    p_charts = sub.add_parser("charts", parents=[common_parser()], help="browse public top/new charts")
    p_charts.add_argument("feed", choices=sorted(CHART_FEEDS),
                          help="top-free | top-paid | top-grossing | new")
    p_charts.add_argument("-n", "--limit", type=int, default=25, help="entries (1-100)")
    p_charts.add_argument("--genre", help="genre alias or numeric genre id")

    p_compare = sub.add_parser("compare", parents=[common_parser()], help="compare 2+ apps side by side")
    p_compare.add_argument("targets", nargs="+",
                           help="numeric track ids and/or bundle ids, mixed is fine")

    sub.add_parser("genres", parents=[common_parser()], help="list supported genre aliases and numeric ids")

    p_watch = sub.add_parser("watch", parents=[common_parser()], help="local-first watchlist + change snapshots")
    wsub = p_watch.add_subparsers(dest="watch_command", metavar="<action>")

    w_add = wsub.add_parser("add", help="look up an app and add it to the watchlist")
    w_add.add_argument("target", help="numeric track id or bundle id")

    w_rm = wsub.add_parser("rm", help="remove an app from the watchlist")
    w_rm.add_argument("track_id", type=int)

    wsub.add_parser("ls", help="list watched apps")

    w_snap = wsub.add_parser("snapshot", help="fetch fresh metadata for watched apps")
    w_snap.add_argument("--id", dest="track_id", type=int, help="snapshot only one app")

    w_diff = wsub.add_parser("diff", help="show changes between the last two snapshots")
    w_diff.add_argument("--id", dest="track_id", type=int, help="diff only one app")

    return parser


def make_client(args: argparse.Namespace) -> AppStoreClient:
    cache = None
    if not getattr(args, "no_cache", False):
        cache = DiskCache(default_cache_dir())
    http = HttpClient(timeout=args.timeout, cache=cache)
    return AppStoreClient(http=http, use_cache=not args.no_cache)


def make_store(args: argparse.Namespace) -> WatchStore:
    if getattr(args, "data_dir", None):
        path = f"{args.data_dir.rstrip('/')}/watchlist.json"
        return WatchStore(path)
    return WatchStore()


def emit(args: argparse.Namespace, text: str) -> None:
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="") as handle:
            handle.write(text + "\n")
        print(f"[asoscope] written to {args.output}", file=sys.stderr)
    else:
        print(text)


def app_rows(apps: Sequence[Any]) -> List[Dict[str, Any]]:
    return [app.to_dict() for app in apps]


def vertical_app(app: Any) -> List[Dict[str, str]]:
    data = app.to_dict()
    labels = {
        "track_id": "ID",
        "track_name": "Name",
        "bundle_id": "Bundle ID",
        "developer": "Developer",
        "seller": "Seller",
        "version": "Version",
        "price": "Price (Raw)",
        "formatted_price": "Price",
        "currency": "Currency",
        "is_free": "Free",
        "average_rating": "Rating",
        "rating_count": "Ratings",
        "average_rating_current": "Rating (Current Ver.)",
        "rating_count_current": "Ratings (Current Ver.)",
        "primary_genre": "Primary Genre",
        "genres": "Genres",
        "content_rating": "Content Rating",
        "size_mb": "Size (MB)",
        "minimum_os": "Minimum OS",
        "languages": "Languages",
        "release_date": "Release Date",
        "current_version_release_date": "Current Version Date",
        "release_notes": "Release Notes",
        "country": "Store",
        "url": "URL",
        "icon_url": "Icon URL",
        "description": "Description",
    }
    rows: List[Dict[str, str]] = []
    preferred = [
        "track_id", "track_name", "bundle_id", "developer", "seller", "version",
        "price", "formatted_price", "currency", "is_free", "average_rating",
        "rating_count", "average_rating_current", "rating_count_current",
        "primary_genre", "genres", "content_rating", "size_mb", "minimum_os",
        "languages", "release_date", "current_version_release_date", "release_notes",
        "country", "url", "icon_url", "description",
    ]
    for key in preferred:
        if key == "size_mb":
            value = app.size_mb
        elif key == "is_free":
            value = app.is_free
        else:
            value = data.get(key)
        rows.append({"field": labels.get(key, key), "value": "" if value is None else value})
    return rows

def resolve_target(client: AppStoreClient, target: str, country: str) -> Any:
    target = target.strip()
    if target.isdigit():
        return client.lookup(country=country, track_id=int(target))
    return client.lookup(country=country, bundle_id=target)


# ---- command handlers ----------------------------------------------------

def cmd_search(client: AppStoreClient, args: argparse.Namespace) -> str:
    apps = client.search(
        args.term, country=args.country, limit=args.limit, device=args.device,
        genre=args.genre, price=args.price, min_rating=args.min_rating, sort=args.sort,
    )
    return render(app_rows(apps), APP_COLUMNS, args.format)


def cmd_lookup(client: AppStoreClient, args: argparse.Namespace) -> str:
    app = client.lookup(country=args.country, track_id=args.track_id,
                        bundle_id=args.bundle_id)
    if args.format == "json":
        import json
        return json.dumps(app.to_dict(), ensure_ascii=False, indent=2)
    rows = vertical_app(app)
    if args.format == "table":
        for row in rows:
            row["value"] = truncate(str(row["value"]), 100)
    return render(rows, [("field", "Field"), ("value", "Value")], args.format)


def cmd_reviews(client: AppStoreClient, args: argparse.Namespace) -> str:
    reviews = client.reviews(args.track_id, country=args.country,
                             page=args.page, sort=args.sort)
    if args.stats:
        counter = Counter(r.rating for r in reviews)
        total = sum(counter.values())
        avg = round(sum(r.rating for r in reviews) / total, 3) if total else 0.0
        rows = [
            {"metric": "reviews_on_page", "value": total},
            {"metric": "average_stars", "value": avg},
        ]
        for stars in range(5, 0, -1):
            rows.append({"metric": f"{stars}_star", "value": counter.get(stars, 0)})
        return render(rows, [("metric", "Metric"), ("value", "Value")], args.format)
    return render([r.to_dict() for r in reviews], REVIEW_COLUMNS, args.format)


def cmd_charts(client: AppStoreClient, args: argparse.Namespace) -> str:
    entries = client.chart(args.feed, country=args.country,
                           limit=args.limit, genre=args.genre)
    return render([e.to_dict() for e in entries], CHART_COLUMNS, args.format)


def cmd_compare(client: AppStoreClient, args: argparse.Namespace) -> str:
    apps = client.compare(args.targets, country=args.country)
    return render(app_rows(apps), APP_COLUMNS, args.format)


def cmd_genres(client: AppStoreClient, args: argparse.Namespace) -> str:
    rows = [{"alias": alias, "genre_id": gid} for alias, gid in sorted(GENRES.items())]
    return render(rows, [("alias", "Alias"), ("genre_id", "Genre ID")], args.format)


def cmd_watch(client: AppStoreClient, store: WatchStore, args: argparse.Namespace) -> str:
    action = args.watch_command
    if action is None:
        raise AScopeError("watch requires an action: add | rm | ls | snapshot | diff")

    if action == "add":
        app = resolve_target(client, args.target, normalize_country(args.country))
        created = store.add(app.snapshot())
        status = "added" if created else "already-watched"
        return render([{"track_id": app.track_id, "track_name": app.track_name,
                        "bundle_id": app.bundle_id, "status": status}],
                      [("track_id", "ID"), ("track_name", "Name"),
                       ("bundle_id", "Bundle ID"), ("status", "Status")], args.format)

    if action == "rm":
        removed = store.remove(args.track_id)
        return render([{"track_id": removed["track_id"], "track_name": removed.get("track_name", ""),
                        "status": "removed"}],
                      [("track_id", "ID"), ("track_name", "Name"), ("status", "Status")],
                      args.format)

    if action == "ls":
        return render(store.list(), WATCH_COLUMNS, args.format)

    if action == "snapshot":
        ids = [args.track_id] if args.track_id else store.tracked_ids()
        rows = []
        for track_id in ids:
            record = store.get(track_id)
            cc = record.get("country") or args.country
            app = client.lookup(country=cc, track_id=track_id)
            before = len(record.get("snapshots", []))
            store.append_snapshot(app.snapshot())
            after = before + 1
            rows.append({"track_id": app.track_id, "track_name": app.track_name,
                         "version": app.version, "price": app.formatted_price,
                         "average_rating": app.average_rating,
                         "rating_count": app.rating_count, "snapshots_total": after})
        return render(rows, [
            ("track_id", "ID"), ("track_name", "Name"), ("version", "Version"),
            ("price", "Price"), ("average_rating", "Rating"),
            ("rating_count", "Ratings"), ("snapshots_total", "Snapshots"),
        ], args.format)

    # action == "diff"
    target_ids = [args.track_id] if args.track_id else store.tracked_ids()
    rows: List[Dict[str, Any]] = []
    for track_id in target_ids:
        result = store.diff(track_id)
        for field_name, change in result["changes"].items():
            rows.append({"track_id": track_id, "track_name": result["track_name"],
                         "field": field_name, "old": change["old"], "new": change["new"]})
    if not rows:
        return "(no changes between the latest two snapshots)"
    columns = [("track_id", "ID"), ("track_name", "Name")] + DIFF_COLUMNS
    return render(rows, columns, args.format)


HANDLERS = {
    "search": cmd_search,
    "lookup": cmd_lookup,
    "reviews": cmd_reviews,
    "charts": cmd_charts,
    "compare": cmd_compare,
    "genres": cmd_genres,
}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 2

    try:
        country = normalize_country(args.country)
        args.country = country
        client = make_client(args)
        if args.command == "watch":
            store = make_store(args)
            text = cmd_watch(client, store, args)
        else:
            handler = HANDLERS[args.command]
            text = handler(client, args)
        emit(args, text)
        return 0
    except AScopeError as exc:
        print(f"asoscope: error: {exc}", file=sys.stderr)
        return exc.exit_code
    except KeyboardInterrupt:  # pragma: no cover - interactive only
        print("asoscope: interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
