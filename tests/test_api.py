import json
import os
import unittest
from urllib.parse import parse_qs, urlparse

from asoscope.api import (
    AppStoreClient,
    build_chart_url,
    build_lookup_url,
    build_reviews_url,
    build_search_url,
    resolve_genre,
)
from asoscope.errors import NotFoundError, UsageError

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as handle:
        return json.load(handle)


class FixtureHttp:
    """Route built URLs back to captured Apple responses — never online."""

    def __init__(self):
        self.requested = []

    def get_json(self, url, use_cache=True):
        self.requested.append(url)
        path = urlparse(url).path
        query = parse_qs(urlparse(url).query)
        if path == "/search":
            return load_fixture("search_minecraft_us.json")
        if path == "/lookup":
            if query.get("bundleId") == ["com.mojang.minecraftpe"] or "id" in query:
                return load_fixture("lookup_bundle.json")
            return {"resultCount": 0, "results": []}
        if "customerreviews" in path:
            return load_fixture("reviews_github.json")
        if "topfreeapplications" in path:
            return load_fixture("charts_topfree_us.json")
        if "newapplications" in path:
            return load_fixture("charts_new_jp.json")
        raise AssertionError(f"unexpected url: {url}")


class UrlBuilderTests(unittest.TestCase):
    def test_search_url_params(self):
        url = build_search_url("habit tracker", "jp", 10, "ipad", resolve_genre("productivity"))
        q = parse_qs(urlparse(url).query)
        self.assertEqual(q["term"], ["habit tracker"])
        self.assertEqual(q["country"], ["jp"])
        self.assertEqual(q["entity"], ["iPadSoftware"])
        self.assertEqual(q["genreId"], ["6007"])
        self.assertEqual(q["limit"], ["10"])

    def test_lookup_requires_identifier(self):
        with self.assertRaises(UsageError):
            build_lookup_url()

    def test_reviews_url(self):
        url = build_reviews_url(123, "us", 2, "helpful")
        self.assertIn("page=2", url)
        self.assertIn("id=123", url)
        self.assertIn("sortby=mostHelpful", url)

    def test_chart_url_caps_limit_and_genre(self):
        url = build_chart_url("top-free", "de", 999, resolve_genre("games"))
        self.assertIn("/de/rss/topfreeapplications/", url)
        self.assertIn("limit=100", url)
        self.assertIn("genre=6014/", url)

    def test_resolve_genre_rejects_unknown(self):
        with self.assertRaises(UsageError):
            resolve_genre("not-a-genre")
        self.assertEqual(resolve_genre("6007"), 6007)
        self.assertIsNone(resolve_genre(None))


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.client = AppStoreClient(http=FixtureHttp())

    def test_search_parsing_and_filters(self):
        apps = self.client.search("minecraft", country="us")
        self.assertTrue(apps)
        self.assertEqual(apps[0].country, "us")
        free = self.client.search("minecraft", price="free")
        self.assertTrue(all(a.is_free for a in free))
        top = self.client.search("minecraft", sort="rating")
        ratings = [a.average_rating or 0 for a in top]
        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_lookup_by_bundle(self):
        app = self.client.lookup(bundle_id="com.mojang.minecraftpe")
        self.assertEqual(app.bundle_id, "com.mojang.minecraftpe")

    def test_lookup_missing_raises(self):
        with self.assertRaises(NotFoundError):
            self.client.lookup(bundle_id="does.not.exist")

    def test_reviews(self):
        reviews = self.client.reviews(1477376905)
        self.assertEqual(len(reviews), 50)
        self.assertTrue(all(0 <= r.rating <= 5 for r in reviews))

    def test_chart_respects_limit(self):
        entries = self.client.chart("top-free", limit=3)
        self.assertEqual(len(entries), 3)
        self.assertEqual([e.rank for e in entries], [1, 2, 3])

    def test_compare_needs_two(self):
        with self.assertRaises(UsageError):
            self.client.compare(["only-one"])

    def test_compare_mixed_ids(self):
        apps = self.client.compare(["123", "com.mojang.minecraftpe"])
        self.assertEqual(len(apps), 2)


if __name__ == "__main__":
    unittest.main()
