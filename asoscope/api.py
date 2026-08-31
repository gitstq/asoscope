"""Client for Apple's public iTunes Search API and public RSS feeds.

Endpoint reference (all public, keyless, read-only):
* Search / Lookup — https://itunes.apple.com/search | /lookup
* Charts          — https://itunes.apple.com/{cc}/rss/{feed}/limit={n}/json
* Reviews         — https://itunes.apple.com/{cc}/rss/customerreviews/...

asoscope never authenticates, never calls private App Store endpoints and
never downloads IPA binaries.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from .errors import NotFoundError, UsageError
from .http import HttpClient
from .models import App, ChartEntry, Review

# Curated, stable subset of iOS App Store category ids (public Apple values).
GENRES: Dict[str, int] = {
    "business": 6000,
    "weather": 6001,
    "utilities": 6002,
    "travel": 6003,
    "sports": 6004,
    "social": 6005,
    "social-networking": 6005,
    "reference": 6006,
    "productivity": 6007,
    "photo-video": 6008,
    "news": 6009,
    "navigation": 6010,
    "music": 6011,
    "lifestyle": 6012,
    "health-fitness": 6013,
    "games": 6014,
    "finance": 6015,
    "entertainment": 6016,
    "education": 6017,
    "books": 6018,
    "medical": 6020,
    "food-drink": 6023,
    "shopping": 6024,
    "developer-tools": 6026,
    "graphics-design": 6027,
}

# Public RSS chart feeds, keyed by short CLI alias.
CHART_FEEDS: Dict[str, str] = {
    "top-free": "topfreeapplications",
    "top-paid": "toppaidapplications",
    "top-grossing": "topgrossingapplications",
    "new": "newapplications",
}

REVIEW_SORTS = {"recent": "mostRecent", "helpful": "mostHelpful"}
DEVICES = {"iphone": "software", "ipad": "iPadSoftware", "any": "software"}


def normalize_country(country: str) -> str:
    cc = (country or "us").strip().lower()
    if len(cc) != 2 or not cc.isalpha():
        raise UsageError(f"Invalid App Store country code: {country!r} (expect ISO 3166-1 alpha-2)")
    return cc


def resolve_genre(genre: Optional[str]) -> Optional[int]:
    """Resolve a genre alias / numeric string to Apple's numeric genre id."""
    if genre is None or str(genre).strip() == "":
        return None
    raw = str(genre).strip().lower()
    if raw in GENRES:
        return GENRES[raw]
    if raw.isdigit():
        return int(raw)
    raise UsageError(
        f"Unknown genre {genre!r}. Use an alias like 'games' or a numeric genre id."
    )


def build_search_url(
    term: str,
    country: str = "us",
    limit: int = 20,
    device: str = "iphone",
    genre_id: Optional[int] = None,
) -> str:
    params: Dict[str, Any] = {
        "term": term,
        "country": country,
        "media": "software",
        "entity": DEVICES.get(device, "software"),
        "limit": limit,
    }
    if genre_id is not None:
        params["genreId"] = genre_id
    return "https://itunes.apple.com/search?" + urlencode(params)


def build_lookup_url(
    country: str = "us",
    track_id: Optional[int] = None,
    bundle_id: Optional[str] = None,
) -> str:
    params: Dict[str, str] = {"country": country}
    if track_id is not None:
        params["id"] = str(track_id)
    elif bundle_id:
        params["bundleId"] = bundle_id
    else:
        raise UsageError("lookup requires either a track id or a bundle id")
    return "https://itunes.apple.com/lookup?" + urlencode(params)


def build_reviews_url(
    track_id: int,
    country: str = "us",
    page: int = 1,
    sort: str = "recent",
) -> str:
    if sort not in REVIEW_SORTS:
        raise UsageError(f"review sort must be one of {sorted(REVIEW_SORTS)}")
    page = max(1, page)
    return (
        f"https://itunes.apple.com/{country}/rss/customerreviews/"
        f"page={page}/id={int(track_id)}/sortby={REVIEW_SORTS[sort]}/json"
    )


def build_chart_url(
    feed: str,
    country: str = "us",
    limit: int = 25,
    genre_id: Optional[int] = None,
) -> str:
    if feed not in CHART_FEEDS:
        raise UsageError(f"chart feed must be one of {sorted(CHART_FEEDS)}")
    limit = max(1, min(limit, 100))
    suffix = f"genre={genre_id}/" if genre_id is not None else ""
    return (
        f"https://itunes.apple.com/{country}/rss/{CHART_FEEDS[feed]}/"
        f"limit={limit}/{suffix}json"
    )


class AppStoreClient:
    """High-level operations over the public Apple endpoints."""

    def __init__(self, http: Optional[HttpClient] = None, use_cache: bool = True):
        self.http = http or HttpClient()
        self.use_cache = use_cache

    # ---- core endpoints -------------------------------------------------

    def search_raw(self, term: str, country: str = "us", limit: int = 20,
                   device: str = "iphone", genre: Optional[str] = None) -> List[App]:
        cc = normalize_country(country)
        genre_id = resolve_genre(genre)
        limit = max(1, min(limit, 200))
        url = build_search_url(term, cc, limit, device, genre_id)
        payload = self.http.get_json(url, use_cache=self.use_cache)
        return [App.from_payload(row, cc) for row in payload.get("results", [])]

    def search(self, term: str, country: str = "us", limit: int = 20,
               device: str = "iphone", genre: Optional[str] = None,
               price: Optional[str] = None, min_rating: Optional[float] = None,
               sort: str = "relevance") -> List[App]:
        apps = self.search_raw(term, country, limit, device, genre)
        if price == "free":
            apps = [a for a in apps if a.is_free]
        elif price == "paid":
            apps = [a for a in apps if not a.is_free]
        elif price not in (None, "", "all"):
            raise UsageError("price filter must be 'free', 'paid' or 'all'")
        if min_rating is not None:
            apps = [a for a in apps if (a.average_rating or 0.0) >= float(min_rating)]
        if sort == "rating":
            apps.sort(key=lambda a: (a.average_rating or 0.0), reverse=True)
        elif sort == "ratings":
            apps.sort(key=lambda a: a.rating_count, reverse=True)
        elif sort == "name":
            apps.sort(key=lambda a: a.track_name.lower())
        elif sort not in ("relevance", "", None):
            raise UsageError("sort must be one of relevance|rating|ratings|name")
        return apps

    def lookup(self, country: str = "us", track_id: Optional[int] = None,
               bundle_id: Optional[str] = None) -> App:
        cc = normalize_country(country)
        url = build_lookup_url(cc, track_id, bundle_id)
        payload = self.http.get_json(url, use_cache=self.use_cache)
        results = payload.get("results") or []
        if not results:
            target = f"id={track_id}" if track_id else f"bundleId={bundle_id}"
            raise NotFoundError(f"No app found for {target} in the {cc.upper()} storefront")
        return App.from_payload(results[0], cc)

    def reviews(self, track_id: int, country: str = "us", page: int = 1,
                sort: str = "recent") -> List[Review]:
        cc = normalize_country(country)
        url = build_reviews_url(track_id, cc, page, sort)
        payload = self.http.get_json(url, use_cache=self.use_cache)
        feed = payload.get("feed") or {}
        entries = feed.get("entry") or []
        # When an app has no reviews Apple sometimes returns a single dict
        # describing the absence rather than a list of review entries.
        if isinstance(entries, dict):
            entries = []
        return [Review.from_entry(entry) for entry in entries]

    def chart(self, feed: str, country: str = "us", limit: int = 25,
              genre: Optional[str] = None) -> List[ChartEntry]:
        cc = normalize_country(country)
        genre_id = resolve_genre(genre)
        url = build_chart_url(feed, cc, limit, genre_id)
        payload = self.http.get_json(url, use_cache=self.use_cache)
        entries = (payload.get("feed") or {}).get("entry") or []
        if isinstance(entries, dict):
            entries = [entries]
        rows: List[ChartEntry] = []
        for index, entry in enumerate(entries, start=1):
            rows.append(ChartEntry.from_entry(entry, index))
            if len(rows) >= max(1, min(limit, 100)):
                break
        return rows

    # ---- derived operations --------------------------------------------

    def compare(self, targets: List[str], country: str = "us") -> List[App]:
        """Resolve a mixed list of numeric ids / bundle ids to apps."""
        if len(targets) < 2:
            raise UsageError("compare needs at least two app ids or bundle ids")
        apps: List[App] = []
        for target in targets:
            target = target.strip()
            if target.isdigit():
                apps.append(self.lookup(country=country, track_id=int(target)))
            else:
                apps.append(self.lookup(country=country, bundle_id=target))
        return apps
