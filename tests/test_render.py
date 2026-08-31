import csv
import io
import unittest

from asoscope.render import render, render_json, render_markdown, render_table, render_csv
from asoscope.text import display_width

COLUMNS = [("id", "ID"), ("name", "Name")]
ROWS = [
    {"id": 1, "name": "GitHub"},
    {"id": 2, "name": "微信"},  # CJK: 4 columns wide
]


class RenderTests(unittest.TestCase):
    def test_table_columns_align_with_cjk(self):
        out = render_table(ROWS, COLUMNS)
        lines = out.splitlines()
        # Header and every data row must share the same visible width.
        widths = {display_width(line) for line in lines}
        self.assertEqual(len(widths), 1, out)

    def test_json_roundtrip(self):
        import json
        out = render_json(ROWS)
        self.assertEqual(json.loads(out), ROWS)

    def test_csv_has_header_and_rows(self):
        out = render_csv(ROWS, COLUMNS)
        reader = list(csv.reader(io.StringIO(out)))
        self.assertEqual(reader[0], ["ID", "Name"])
        self.assertEqual(len(reader), 3)

    def test_markdown_escapes_pipes(self):
        out = render_markdown([{"id": 1, "name": "a|b"}], COLUMNS)
        self.assertIn("a\\|b", out)
        self.assertEqual(len(out.splitlines()), 3)

    def test_empty_rows_table(self):
        self.assertEqual(render_table([], COLUMNS), "(no rows)")

    def test_dispatch(self):
        self.assertIn("GitHub", render(ROWS, COLUMNS, "md"))
        with self.assertRaises(ValueError):
            render(ROWS, COLUMNS, "yaml")


if __name__ == "__main__":
    unittest.main()
