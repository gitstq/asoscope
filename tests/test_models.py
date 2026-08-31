import json
import os
import unittest

from asoscope.models import App, ChartEntry, Review

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as handle:
        return json.load(handle)


class AppModelTests(unittest.TestCase):
    def test_parse_search_payload(self):
        payload = load_fixture("search_minecraft_us.json")
        app = App.from_payload(payload["results"][0], "us")
        self.assertTrue(app.track_id > 0)
        self.assertTrue(app.track_name)
        self.assertEqual(app.bundle_id, "com.mojang.minecraftpe")
        self.assertIsInstance(app.genres, list)
        self.assertTrue(app.file_size_bytes > 0)
        self.assertIsNotNone(app.size_mb)

    def test_parse_lookup_by_bundle(self):
        payload = load_fixture("lookup_bundle.json")
        self.assertEqual(payload["resultCount"], 1)
        app = App.from_payload(payload["results"][0])
        self.assertEqual(app.bundle_id, "com.mojang.minecraftpe")
        snap = app.snapshot()
        for key in ("track_id", "version", "price", "average_rating", "rating_count"):
            self.assertIn(key, snap)

    def test_bad_numeric_input_never_raises(self):
        app = App.from_payload({"trackId": None, "averageUserRating": "oops",
                                "fileSizeBytes": "", "genres": None})
        self.assertEqual(app.track_id, 0)
        self.assertIsNone(app.average_rating)
        self.assertEqual(app.file_size_bytes, 0)
        self.assertEqual(app.genres, [])


class ReviewModelTests(unittest.TestCase):
    def test_parse_review_entries(self):
        payload = load_fixture("reviews_github.json")
        entries = payload["feed"]["entry"]
        reviews = [Review.from_entry(e) for e in entries]
        self.assertEqual(len(reviews), 50)
        first = reviews[0]
        self.assertTrue(first.review_id)
        self.assertIn(first.rating, range(0, 6))
        self.assertTrue(first.author)


class ChartModelTests(unittest.TestCase):
    def test_parse_chart_entries_ranked(self):
        payload = load_fixture("charts_topfree_us.json")
        entries = payload["feed"]["entry"]
        rows = [ChartEntry.from_entry(e, i) for i, e in enumerate(entries, 1)]
        self.assertEqual(rows[0].rank, 1)
        self.assertTrue(rows[0].track_name)
        self.assertTrue(all(r.rank >= 1 for r in rows))

    def test_list_link_and_toplevel_price_variant(self):
        # Some storefronts (e.g. German feed) return link as a list and put
        # the human-readable price label on the node itself.
        entry = {
            "im:name": {"label": "Demo"},
            "im:artist": {"label": "Maker"},
            "id": {"label": "https://apps.apple.com/de/app/demo/id123",
                   "attributes": {"im:id": "123"}},
            "link": [
                {"attributes": {"rel": "enclosure", "type": "image/jpeg",
                                "href": "https://img.example/x.jpg"}},
                {"attributes": {"rel": "alternate", "type": "text/html",
                                "href": "https://apps.apple.com/de/app/demo/id123"}},
            ],
            "im:price": {"label": "Laden",
                         "attributes": {"amount": "0.00", "currency": "EUR"}},
            "category": {"attributes": {"label": "Produktivität"}},
        }
        row = ChartEntry.from_entry(entry, 1)
        self.assertEqual(row.track_id, 123)
        self.assertEqual(row.url, "https://apps.apple.com/de/app/demo/id123")
        self.assertEqual(row.price_label, "Laden")
        self.assertEqual(row.category, "Produktivität")


if __name__ == "__main__":
    unittest.main()
