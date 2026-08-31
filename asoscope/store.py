"""Local-first watchlist and snapshot store.

State lives in a single human-readable JSON file under the per-OS user
data directory. Nothing is ever uploaded: asoscope has no telemetry and
no server side.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .errors import NotFoundError, StoreError

# Fields compared when diffing two snapshots.
DIFF_FIELDS: Tuple[str, ...] = (
    "version",
    "price",
    "formatted_price",
    "average_rating",
    "rating_count",
    "file_size_bytes",
    "current_version_release_date",
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_data_dir() -> str:
    """Return the platform-appropriate writable data directory."""
    override = os.environ.get("ASOSCOPE_DATA_DIR")
    if override:
        return override
    app = "asoscope"
    if sys.platform == "win32":
        root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(root, app)
    if sys.platform == "darwin":
        return os.path.expanduser(os.path.join("~", "Library", "Application Support", app))
    root = os.environ.get("XDG_DATA_HOME") or os.path.expanduser(os.path.join("~", ".local", "share"))
    return os.path.join(root, app)


def default_cache_dir() -> str:
    """Return the platform-appropriate writable cache directory."""
    override = os.environ.get("ASOSCOPE_CACHE_DIR")
    if override:
        return override
    app = "asoscope"
    if sys.platform == "win32":
        root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(root, app, "cache")
    if sys.platform == "darwin":
        return os.path.expanduser(os.path.join("~", "Library", "Caches", app))
    root = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser(os.path.join("~", ".cache"))
    return os.path.join(root, app)


class WatchStore:
    """JSON-backed watchlist with append-only metadata snapshots."""

    SCHEMA_VERSION = 1

    def __init__(self, path: Optional[str] = None):
        self.path = path or os.path.join(default_data_dir(), "watchlist.json")
        self._state: Dict[str, Any] = {"schema": self.SCHEMA_VERSION, "apps": {}}
        self.load()

    # ---- persistence ----------------------------------------------------

    def load(self) -> None:
        if not os.path.exists(self.path):
            self._state = {"schema": self.SCHEMA_VERSION, "apps": {}}
            return
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                state = json.load(handle)
            if not isinstance(state, dict) or "apps" not in state:
                raise StoreError(f"Watchlist file is malformed: {self.path}")
            self._state = state
        except (OSError, ValueError) as exc:
            raise StoreError(f"Unable to read watchlist {self.path}: {exc}") from exc

    def save(self) -> None:
        directory = os.path.dirname(self.path) or "."
        try:
            os.makedirs(directory, exist_ok=True)
            fd, tmp = tempfile.mkstemp(prefix=".watchlist-", suffix=".json", dir=directory)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(self._state, handle, ensure_ascii=False, indent=2, sort_keys=True)
            os.replace(tmp, self.path)
        except OSError as exc:
            raise StoreError(f"Unable to write watchlist {self.path}: {exc}") from exc

    # ---- watchlist management ------------------------------------------

    def _key(self, track_id: int) -> str:
        return str(int(track_id))

    def add(self, app_snapshot: Dict[str, Any]) -> bool:
        """Add an app. Returns False if it was already watched."""
        key = self._key(int(app_snapshot["track_id"]))
        apps = self._state["apps"]
        if key in apps:
            return False
        record = {
            "track_id": int(app_snapshot["track_id"]),
            "track_name": app_snapshot.get("track_name", ""),
            "bundle_id": app_snapshot.get("bundle_id", ""),
            "country": app_snapshot.get("country", ""),
            "added_at": utc_now_iso(),
            "snapshots": [],
        }
        record["snapshots"].append({"at": utc_now_iso(), **deepcopy(app_snapshot)})
        apps[key] = record
        self.save()
        return True

    def remove(self, track_id: int) -> Dict[str, Any]:
        key = self._key(track_id)
        apps = self._state["apps"]
        if key not in apps:
            raise NotFoundError(f"App {track_id} is not on the watchlist")
        removed = apps.pop(key)
        self.save()
        return removed

    def list(self) -> List[Dict[str, Any]]:
        rows = []
        for record in self._state["apps"].values():
            latest = record["snapshots"][-1] if record.get("snapshots") else {}
            rows.append(
                {
                    "track_id": record["track_id"],
                    "track_name": record.get("track_name", ""),
                    "bundle_id": record.get("bundle_id", ""),
                    "country": record.get("country", ""),
                    "added_at": record.get("added_at", ""),
                    "snapshot_count": len(record.get("snapshots", [])),
                    "latest": latest,
                }
            )
        rows.sort(key=lambda r: r["track_name"].lower())
        return rows

    def tracked_ids(self) -> List[int]:
        return [int(k) for k in self._state["apps"].keys()]

    def get(self, track_id: int) -> Dict[str, Any]:
        key = self._key(track_id)
        if key not in self._state["apps"]:
            raise NotFoundError(f"App {track_id} is not on the watchlist")
        return self._state["apps"][key]

    # ---- snapshots & diff ----------------------------------------------

    def append_snapshot(self, app_snapshot: Dict[str, Any]) -> None:
        key = self._key(int(app_snapshot["track_id"]))
        apps = self._state["apps"]
        if key not in apps:
            self.add(app_snapshot)
            return
        record = apps[key]
        record["track_name"] = app_snapshot.get("track_name", record.get("track_name", ""))
        record["snapshots"].append({"at": utc_now_iso(), **deepcopy(app_snapshot)})
        self.save()

    @staticmethod
    def diff_snapshots(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Return ``{field: {"old": x, "new": y}}`` for every changed field."""
        changes: Dict[str, Dict[str, Any]] = {}
        for field_name in DIFF_FIELDS:
            if old.get(field_name) != new.get(field_name):
                changes[field_name] = {"old": old.get(field_name), "new": new.get(field_name)}
        return changes

    def diff(self, track_id: int) -> Dict[str, Any]:
        record = self.get(track_id)
        snaps = record.get("snapshots", [])
        if len(snaps) < 2:
            return {"track_id": track_id, "track_name": record.get("track_name", ""),
                    "changes": {}, "previous_at": None, "latest_at": snaps[-1]["at"] if snaps else None}
        previous, latest = snaps[-2], snaps[-1]
        return {
            "track_id": track_id,
            "track_name": record.get("track_name", ""),
            "previous_at": previous.get("at"),
            "latest_at": latest.get("at"),
            "changes": self.diff_snapshots(previous, latest),
        }
