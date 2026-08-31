"""Normalized domain models.

Apple returns three slightly different payload shapes (search/lookup,
customer-review RSS, chart RSS). :class:`App`, :class:`Review` and
:class:`ChartEntry` collapse them into stable, documented structures so
the rest of the codebase never touches raw Apple field names.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


def _num(value: Any, default: float = 0.0) -> float:
    """Best-effort numeric coercion that never raises on bad input."""
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _str(value: Any, default: str = "") -> str:
    return default if value is None else str(value)


def _opt_float(value: Any, digits: int = 2) -> Optional[float]:
    """Coerce to a rounded float, returning None if missing or unparsable."""
    if value is None or value == "":
        return None
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None


@dataclass
class App:
    """A normalized App Store application record."""

    track_id: int
    track_name: str
    bundle_id: str = ""
    developer: str = ""
    developer_id: int = 0
    version: str = ""
    price: float = 0.0
    formatted_price: str = ""
    currency: str = ""
    average_rating: Optional[float] = None
    rating_count: int = 0
    average_rating_current: Optional[float] = None
    rating_count_current: int = 0
    primary_genre: str = ""
    primary_genre_id: int = 0
    genres: List[str] = field(default_factory=list)
    content_rating: str = ""
    file_size_bytes: int = 0
    minimum_os: str = ""
    release_date: str = ""
    current_version_release_date: str = ""
    release_notes: str = ""
    description: str = ""
    seller: str = ""
    languages: List[str] = field(default_factory=list)
    country: str = ""
    url: str = ""
    icon_url: str = ""

    @property
    def is_free(self) -> bool:
        return self.price == 0.0

    @property
    def size_mb(self) -> Optional[float]:
        if not self.file_size_bytes:
            return None
        return round(self.file_size_bytes / (1024 * 1024), 2)

    @classmethod
    def from_payload(cls, payload: Dict[str, Any], country: str = "") -> "App":
        return cls(
            track_id=int(_num(payload.get("trackId"), 0)),
            track_name=_str(payload.get("trackName")),
            bundle_id=_str(payload.get("bundleId")),
            developer=_str(payload.get("artistName")),
            developer_id=int(_num(payload.get("artistId"), 0)),
            version=_str(payload.get("version")),
            price=_num(payload.get("price"), 0.0),
            formatted_price=_str(payload.get("formattedPrice")),
            currency=_str(payload.get("currency")),
            average_rating=_opt_float(payload.get("averageUserRating")),
            rating_count=int(_num(payload.get("userRatingCount"), 0)),
            average_rating_current=_opt_float(
                payload.get("averageUserRatingForCurrentVersion")
            ),
            rating_count_current=int(
                _num(payload.get("userRatingCountForCurrentVersion"), 0)
            ),
            primary_genre=_str(payload.get("primaryGenreName")),
            primary_genre_id=int(_num(payload.get("primaryGenreId"), 0)),
            genres=list(payload.get("genres") or []),
            content_rating=_str(
                payload.get("contentAdvisoryRating")
                or payload.get("trackContentRating")
            ),
            file_size_bytes=int(_num(payload.get("fileSizeBytes"), 0)),
            minimum_os=_str(payload.get("minimumOsVersion")),
            release_date=_str(payload.get("releaseDate")),
            current_version_release_date=_str(payload.get("currentVersionReleaseDate")),
            release_notes=_str(payload.get("releaseNotes")),
            description=_str(payload.get("description")),
            seller=_str(payload.get("sellerName")),
            languages=list(payload.get("languageCodesISO2A") or []),
            country=country,
            url=_str(payload.get("trackViewUrl")),
            icon_url=_str(payload.get("artworkUrl512") or payload.get("artworkUrl100")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def snapshot(self) -> Dict[str, Any]:
        """Compact, watchlist-relevant state used for change detection."""
        return {
            "track_id": self.track_id,
            "track_name": self.track_name,
            "bundle_id": self.bundle_id,
            "version": self.version,
            "price": self.price,
            "formatted_price": self.formatted_price,
            "average_rating": self.average_rating,
            "rating_count": self.rating_count,
            "file_size_bytes": self.file_size_bytes,
            "current_version_release_date": self.current_version_release_date,
            "country": self.country or self.country,
        }


@dataclass
class Review:
    """A single customer review from the public RSS feed."""

    review_id: str
    title: str
    content: str
    rating: int
    version: str
    author: str
    updated: str
    vote_sum: int = 0
    vote_count: int = 0

    @classmethod
    def from_entry(cls, entry: Dict[str, Any]) -> "Review":
        def label(key: str, default: str = "") -> str:
            node = entry.get(key)
            if isinstance(node, dict):
                return _str(node.get("label"), default)
            return default

        author_node = entry.get("author") or {}
        author = ""
        if isinstance(author_node, dict):
            author = _str((author_node.get("name") or {}).get("label"))
        return cls(
            review_id=label("id"),
            title=label("title"),
            content=label("content"),
            rating=int(_num(label("im:rating"), 0)),
            version=label("im:version"),
            author=author,
            updated=label("updated"),
            vote_sum=int(_num(label("im:voteSum"), 0)),
            vote_count=int(_num(label("im:voteCount"), 0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChartEntry:
    """A ranked application on a public App Store chart RSS feed."""

    rank: int
    track_id: int
    track_name: str
    developer: str
    category: str
    price_label: str
    release_date: str = ""
    url: str = ""
    icon_url: str = ""
    summary: str = ""

    @classmethod
    def from_entry(cls, entry: Dict[str, Any], rank: int) -> "ChartEntry":
        def label(key: str, default: str = "") -> str:
            node = entry.get(key)
            if isinstance(node, dict):
                return _str(node.get("label"), default)
            return default

        track_id = 0
        id_node = entry.get("id") or {}
        if isinstance(id_node, dict):
            track_id = int(_num(id_node.get("label"), 0))
            attrs = id_node.get("attributes") or {}
            if not track_id:
                # Some feeds expose the numeric id inside im:bundleId/id attrs.
                track_id = int(_num(attrs.get("im:id"), 0))
        images = entry.get("im:image") or []
        icon_url = ""
        if isinstance(images, list) and images:
            icon_url = _str(images[-1].get("label"))
        # Some storefronts return a single link dict, others a list of
        # links (alternate html + image enclosure); prefer the html one.
        link = entry.get("link") or {}
        url = ""
        if isinstance(link, dict):
            url = _str((link.get("attributes") or {}).get("href"))
        elif isinstance(link, list):
            for item in link:
                attrs = item.get("attributes") or {}
                if attrs.get("rel") == "alternate" or attrs.get("type") == "text/html":
                    url = _str(attrs.get("href"))
                    break
            if not url and link:
                url = _str(((link[0] or {}).get("attributes") or {}).get("href"))
        category = ""
        cat_node = entry.get("category") or {}
        if isinstance(cat_node, dict):
            category = _str((cat_node.get("attributes") or {}).get("label"))
        price_node = entry.get("im:price") or {}
        price_attrs = price_node.get("attributes") or {} if isinstance(price_node, dict) else {}
        price_label = _str(price_attrs.get("label")) or (
            _str(price_node.get("label")) if isinstance(price_node, dict) else ""
        )
        return cls(
            rank=rank,
            track_id=track_id,
            track_name=label("im:name"),
            developer=label("im:artist"),
            category=category,
            price_label=price_label,
            release_date=label("im:releaseDate"),
            url=url,
            icon_url=icon_url,
            summary=label("summary"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
