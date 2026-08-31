import unittest

from asoscope.text import display_width, pad_right, truncate, char_width


class TextWidthTests(unittest.TestCase):
    def test_ascii_width(self):
        self.assertEqual(display_width("hello"), 5)

    def test_cjk_is_double_width(self):
        self.assertEqual(display_width("你好"), 4)
        self.assertEqual(display_width("a你b"), 4)

    def test_combining_mark_zero_width(self):
        # 'e' + combining acute accent occupies one visual column.
        self.assertEqual(char_width("e"), 1)
        self.assertEqual(char_width("\u0301"), 0)

    def test_pad_right_aligns_cjk(self):
        self.assertEqual(pad_right("你好", 6), "你好  ")
        self.assertEqual(display_width(pad_right("你好", 6)), 6)

    def test_truncate_respects_columns(self):
        # A column is always reserved for the ellipsis when truncating.
        self.assertEqual(truncate("你好world", 5), "你好…")
        self.assertEqual(display_width(truncate("你好world", 5)), 5)
        self.assertEqual(truncate("你好world", 4), "你…")
        self.assertEqual(display_width(truncate("你好world", 4)), 3)
        self.assertEqual(truncate("abc", 10), "abc")
        self.assertEqual(truncate("abcdef", 4), "abc…")
        self.assertEqual(truncate("abc", 0), "")


if __name__ == "__main__":
    unittest.main()
