import os
import tempfile
import unittest

from asoscope.errors import NotFoundError
from asoscope.store import WatchStore


def snap(track_id, version, price=0.0, rating=4.5, count=100, size=1000, name="Demo"):
    return {
        "track_id": track_id,
        "track_name": name,
        "bundle_id": f"com.demo.{track_id}",
        "version": version,
        "price": price,
        "formatted_price": "Free" if price == 0 else f"${price}",
        "average_rating": rating,
        "rating_count": count,
        "file_size_bytes": size,
        "current_version_release_date": "2026-08-01T00:00:00Z",
        "country": "us",
    }


class WatchStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "watchlist.json")
        self.store = WatchStore(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_is_idempotent_and_persists(self):
        self.assertTrue(self.store.add(snap(1, "1.0.0")))
        self.assertFalse(self.store.add(snap(1, "1.0.0")))
        reopened = WatchStore(self.path)
        self.assertEqual(reopened.tracked_ids(), [1])

    def test_remove_missing_raises(self):
        with self.assertRaises(NotFoundError):
            self.store.remove(404)

    def test_snapshot_diff_detects_changes(self):
        self.store.add(snap(7, "1.0.0", rating=4.0, count=10))
        self.store.append_snapshot(snap(7, "1.1.0", rating=4.5, count=18))
        result = self.store.diff(7)
        self.assertIn("version", result["changes"])
        self.assertEqual(result["changes"]["version"]["old"], "1.0.0")
        self.assertEqual(result["changes"]["version"]["new"], "1.1.0")
        self.assertIn("average_rating", result["changes"])

    def test_diff_identical_snapshots_is_empty(self):
        self.store.add(snap(8, "2.0.0"))
        self.store.append_snapshot(snap(8, "2.0.0"))
        self.assertEqual(self.store.diff(8)["changes"], {})

    def test_list_sorted_by_name(self):
        self.store.add(snap(2, "1.0", name="Beta"))
        self.store.add(snap(1, "1.0", name="Alpha"))
        names = [r["track_name"] for r in self.store.list()]
        self.assertEqual(names, ["Alpha", "Beta"])

    def test_corrupt_state_raises_store_error(self):
        from asoscope.errors import StoreError
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write("{not json")
        with self.assertRaises(StoreError):
            WatchStore(self.path)


if __name__ == "__main__":
    unittest.main()
