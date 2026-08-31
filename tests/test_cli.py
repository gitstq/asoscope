import json
import os
import tempfile
import unittest
from contextlib import contextmanager
from io import StringIO
from unittest import mock
from urllib.parse import parse_qs, urlparse

from asoscope.api import AppStoreClient
from asoscope.cli import main

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as handle:
        return json.load(handle)


class CliFixtureHttp:
    def get_json(self, url, use_cache=True):
        path = urlparse(url).path
        query = parse_qs(urlparse(url).query)
        if path == "/search":
            return load_fixture("search_minecraft_us.json")
        if path == "/lookup":
            if query.get("bundleId") == ["com.mojang.minecraftpe"] or "id" in query:
                return {"resultCount": 1,
                        "results": [load_fixture("search_minecraft_us.json")["results"][0]]}
            return {"resultCount": 0, "results": []}
        if "customerreviews" in path:
            return load_fixture("reviews_github.json")
        if "topfreeapplications" in path:
            return load_fixture("charts_topfree_us.json")
        raise AssertionError(url)


@contextmanager
def captured_stdout():
    buf = StringIO()
    with mock.patch("sys.stdout", buf):
        yield buf


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fake = AppStoreClient(http=CliFixtureHttp())

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *argv):
        with mock.patch("asoscope.cli.make_client", return_value=self.fake):
            with captured_stdout() as buf:
                code = main(list(argv))
        return code, buf.getvalue()

    def test_no_command_returns_usage_code(self):
        code, _ = self.run_cli()
        self.assertEqual(code, 2)

    def test_version_flag(self):
        with captured_stdout() as buf:
            with self.assertRaises(SystemExit) as ctx:
                main(["--version"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("asoscope 1.0.0", buf.getvalue())

    def test_search_json(self):
        code, out = self.run_cli("-f", "json", "search", "minecraft")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertTrue(data)
        self.assertIn("track_id", data[0])

    def test_search_markdown(self):
        code, out = self.run_cli("-f", "md", "search", "minecraft")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("| "))

    def test_global_flags_work_in_both_positions(self):
        # Before the subcommand ...
        code, before = self.run_cli("-f", "json", "search", "minecraft", "-n", "1")
        self.assertEqual(code, 0)
        self.assertTrue(before.lstrip().startswith("["))
        # ... and after the subcommand must produce identical JSON.
        code, after = self.run_cli("search", "minecraft", "-n", "1", "-f", "json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(before), json.loads(after))

    def test_lookup_table(self):
        code, out = self.run_cli("lookup", "--bundle", "com.mojang.minecraftpe")
        self.assertEqual(code, 0)
        self.assertIn("Bundle ID", out)

    def test_lookup_missing_exit_code(self):
        class Missing(AppStoreClient):
            def lookup(self, **kwargs):
                from asoscope.errors import NotFoundError
                raise NotFoundError("no app")

        missing = Missing(http=object())
        with mock.patch("asoscope.cli.make_client", return_value=missing):
            with captured_stdout():
                code = main(["lookup", "--id", "999"])
        self.assertEqual(code, 4)

    def test_bad_country_exit_code(self):
        code, _ = self.run_cli("-c", "usa", "genres")
        self.assertEqual(code, 2)

    def test_reviews_stats(self):
        code, out = self.run_cli("reviews", "1477376905", "--stats")
        self.assertEqual(code, 0)
        self.assertIn("average_stars", out)

    def test_charts_limit(self):
        code, out = self.run_cli("-f", "json", "charts", "top-free", "-n", "2")
        self.assertEqual(code, 0)
        self.assertEqual(len(json.loads(out)), 2)

    def test_watch_lifecycle_and_diff(self):
        data_dir = self.tmp.name
        track_id = load_fixture("search_minecraft_us.json")["results"][0]["trackId"]

        code, out = self.run_cli("--data-dir", data_dir, "watch", "add", "com.mojang.minecraftpe")
        self.assertEqual(code, 0)
        self.assertIn("added", out)

        code, out = self.run_cli("--data-dir", data_dir, "watch", "ls")
        self.assertEqual(code, 0)
        self.assertTrue(out.strip())

        code, out = self.run_cli("--data-dir", data_dir, "-f", "json", "watch", "snapshot")
        self.assertEqual(code, 0)
        self.assertEqual(len(json.loads(out)), 1)

        code, out = self.run_cli("--data-dir", data_dir, "watch", "diff")
        self.assertEqual(code, 0)  # identical snapshots -> friendly message

        code, out = self.run_cli("--data-dir", data_dir, "watch", "rm", str(track_id))
        self.assertEqual(code, 0)
        self.assertIn("removed", out)

    def test_output_to_file(self):
        target = os.path.join(self.tmp.name, "out.json")
        code, _ = self.run_cli("-f", "json", "-o", target, "genres")
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(target))
        with open(target, encoding="utf-8") as handle:
            self.assertTrue(json.load(handle))


if __name__ == "__main__":
    unittest.main()
