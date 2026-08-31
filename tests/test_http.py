import io
import json
import os
import tempfile
import time
import unittest
import urllib.error

from asoscope.http import DiskCache, HttpClient
from asoscope.errors import APIError, TransportError


class FakeResponse:
    def __init__(self, body):
        self._body = body.encode("utf-8") if isinstance(body, str) else body
        self.headers = {"Content-Type": "application/json; charset=utf-8"}

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def headers_get_content_charset(self):
        return "utf-8"

    # urllib responses expose ..headers.get_content_charset(); emulate simply.
    class _Headers:
        @staticmethod
        def get_content_charset():
            return "utf-8"


class ScriptedOpener:
    """Opener that returns scripted responses or raises scripted errors."""

    def __init__(self, scripted):
        self.scripted = list(scripted)
        self.calls = 0

    def __call__(self, request):
        item = self.scripted[min(self.calls, len(self.scripted) - 1)]
        self.calls += 1
        if isinstance(item, Exception):
            raise item
        response = FakeResponse(json.dumps(item))
        response.headers = ScriptedOpener._Headers()
        return response

    class _Headers:
        @staticmethod
        def get_content_charset():
            return "utf-8"


def http_error(code):
    return urllib.error.HTTPError("http://example.test", code, "err", {}, io.BytesIO(b""))


class HttpTransportTests(unittest.TestCase):
    def test_success_on_first_try(self):
        opener = ScriptedOpener([{"ok": True}])
        client = HttpClient(opener=opener, sleeper=lambda s: None)
        self.assertEqual(client.get_json("http://example.test"), {"ok": True})
        self.assertEqual(opener.calls, 1)

    def test_retries_then_succeeds(self):
        opener = ScriptedOpener([http_error(503), http_error(502), {"ok": 1}])
        client = HttpClient(opener=opener, sleeper=lambda s: None)
        self.assertEqual(client.get_json("http://example.test"), {"ok": 1})
        self.assertEqual(opener.calls, 3)

    def test_404_fails_fast(self):
        opener = ScriptedOpener([http_error(404)])
        client = HttpClient(opener=opener, sleeper=lambda s: None)
        with self.assertRaises(APIError):
            client.get_json("http://example.test")
        self.assertEqual(opener.calls, 1)

    def test_exhaustion_raises_transport_error(self):
        opener = ScriptedOpener([TimeoutError("boom")])
        client = HttpClient(max_retries=2, opener=opener, sleeper=lambda s: None)
        with self.assertRaises(TransportError):
            client.get_json("http://example.test")
        self.assertEqual(opener.calls, 2)

    def test_disk_cache_hit_avoids_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = DiskCache(tmp, ttl_seconds=60)
            opener = ScriptedOpener([{"v": 1}])
            client = HttpClient(opener=opener, cache=cache, sleeper=lambda s: None)
            client.get_json("http://example.test/a")
            client.get_json("http://example.test/a")
            self.assertEqual(opener.calls, 1)

    def test_disk_cache_expires(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = DiskCache(tmp, ttl_seconds=-1)  # always stale
            opener = ScriptedOpener([{"v": 1}, {"v": 2}])
            client = HttpClient(opener=opener, cache=cache, sleeper=lambda s: None)
            first = client.get_json("http://example.test/b")
            second = client.get_json("http://example.test/b")
            self.assertEqual((first, second), ({"v": 1}, {"v": 2}))
            self.assertEqual(opener.calls, 2)

    def test_cache_disabled_path(self):
        cache = DiskCache(None)
        self.assertIsNone(cache.get("http://x"))
        cache.set("http://x", {})  # should no-op without raising


if __name__ == "__main__":
    unittest.main()
