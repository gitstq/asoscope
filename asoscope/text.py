"""Terminal text helpers that are CJK / emoji aware.

The standard ``str.ljust`` assumes every code point occupies one column,
which misaligns tables containing Chinese / Japanese app names. These
helpers compute a monospace display width using ``unicodedata`` only.
"""

from __future__ import annotations

import unicodedata


def char_width(ch: str) -> int:
    """Return the monospace column width of a single character."""
    if not ch:
        return 0
    # Combining marks and zero-width control characters.
    category = unicodedata.category(ch)
    if category in ("Mn", "Me", "Cf"):
        return 0
    east_asian = unicodedata.east_asian_width(ch)
    # W (Wide) and F (Fullwidth) occupy two columns; so does the Korean
    # compatibility block reported as A (Ambiguous) in many terminals.
    if east_asian in ("W", "F"):
        return 2
    if ord(ch) < 0x20:
        return 0
    return 1


def display_width(text: str) -> int:
    """Return the total monospace column width of ``text``."""
    return sum(char_width(ch) for ch in text)


def truncate(text: str, max_width: int) -> str:
    """Truncate ``text`` to at most ``max_width`` columns, ending with '…'.

    One column is reserved for the ellipsis whenever the full text does
    not fit, so the returned string never exceeds ``max_width``.
    """
    if max_width <= 0:
        return ""
    text = str(text)
    if display_width(text) <= max_width:
        return text
    content_budget = max_width - 1  # reserve a column for the ellipsis
    width = 0
    out: list[str] = []
    for ch in text:
        w = char_width(ch)
        if width + w > content_budget:
            break
        out.append(ch)
        width += w
    return "".join(out) + "…"


def pad_right(text: str, width: int) -> str:
    """Right-pad ``text`` with spaces to ``width`` display columns."""
    gap = width - display_width(text)
    return text + " " * gap if gap > 0 else text


def pad_left(text: str, width: int) -> str:
    """Left-pad ``text`` with spaces to ``width`` display columns."""
    gap = width - display_width(text)
    return " " * gap + text if gap > 0 else text
