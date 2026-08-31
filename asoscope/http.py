"""Minimal JSON HTTP transport built on the Python standard library.

Features:
* configurable timeout and bounded exponential-backoff retries;
* on-disk TTL cache (RFC-independent, fully deterministic);
* an injectable ``opener`` seam so unit tests never touch the network.

Only ``GET`` is required because every Apple endpoint used by asoscope is
a public, read-only JSON endpoint.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Optional

from .errors import APIError, TransportError

Opener = Callable[[urllib.request.Request], Any]


def _default_opener(request: urllib.request.Request) -> Any:
    return urllib.request.urlopen(request)  # pragma: no cover - thin wrapper


class DiskCache:
    """A tiny filesystem TTL cache keyed by URL."""

    def __init__(self, cache_dir: Optional[str], ttl_seconds: int = 3600):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)

    def _path_for(self, url: str) -> Optional[str]:
        if not self.cache_dir:
            return None
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, digest + ".json")

    def get(self, url: str) -> Optional[Any]:
        path = self._path_for(url)
        if not path or not os.path.exists(path):
            return None
        try:
            age = time.time() - os.path.getmtime(path)
            if age > self.ttl_seconds:
                return None
            with open(path, "r", encoding="utf-8") as handle:
                blob = json.load(handle)
            return blob.get("data")
        except (OSError, ValueError):
            return None

    def set(self, url: str, data: Any) -> None:
        path = self._path_for(url)
        if not path:
            return
        try:
            # Atomic write so concurrent processes never see a partial file.
            fd, tmp = tempfile.mkstemp(prefix=".ascope-", dir=self.cache_dir)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump({"url": url, "data": data}, handle)
            os.replace(tmp, path)
        except OSError:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass


class HttpClient:
    """JSON GET client with retries, backoff and optional disk cache."""

    def __init__(
        self,
        user_agent: str = "asoscope/1.0",
        timeout: float = 15.0,
        max_retries: int = 3,
        backoff_base: float = 0.4,
        cache: Optional[DiskCache] = None,
        opener: Opener = _default_opener,
        sleeper: Callable[[float], None] = time.sleep,
    ):
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max(1, max_retries)
        self.backoff_base = backoff_base
        self.cache = cache
        self._opener = opener
        self._sleep = sleeper

    def get_json(self, url: str, use_cache: bool = True) -> Any:
        """Fetch ``url`` and parse the JSON body, with retries + cache."""
        if use_cache and self.cache is not None:
            cached = self.cache.get(url)
            if cached is not None:
                return cached

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "application/json, text/json",
                    "Accept-Language": "en-US,en;q=0.8",
                },
            )
            try:
                with self._opener(request) as response:
                    charset = response.headers.get_content_charset() or "utf-8"
                    body = response.read().decode(charset, errors="replace")
                data = json.loads(body)
                if self.cache is not None:
                    self.cache.set(url, data)
                return data
            except urllib.error.HTTPError as exc:
                # Client errors (except 429) will not heal on retry.
                if exc.code == 404:
                    raise APIError(
                        f"Apple endpoint returned 404 Not Found: {url}",
                        status=404,
                        url=url,
                    ) from exc
                last_error = exc
                if exc.code not in (429, 500, 502, 503, 504) or attempt == self.max_retries:
                    raise APIError(
                        f"Apple endpoint returned HTTP {exc.code} for {url}",
                        status=exc.code,
                        url=url,
                    ) from exc
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
                last_error = exc
                if attempt == self.max_retries:
                    break
            self._sleep(self.backoff_base * (2 ** (attempt - 1)))

        raise TransportError(
            f"Network request failed after {self.max_retries} attempts: {url} "
            f"({last_error})"
        )
