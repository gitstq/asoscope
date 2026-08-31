"""Output renderers: aligned terminal table, JSON, CSV and Markdown.

Every renderer consumes the same shape — a list of dict rows plus an
ordered column specification ``[(key, header), ...]`` — so adding a new
command never requires duplicating serialization logic.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any, Dict, List, Sequence, Tuple

from .text import display_width, pad_right, truncate

Column = Tuple[str, str]
Row = Dict[str, Any]

FORMATS = ("table", "json", "csv", "md", "markdown")


def _stringify(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        # Avoid noisy trailing zeros while keeping floats readable.
        return f"{value:g}"
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    return str(value)


def render_json(rows: Sequence[Row]) -> str:
    return json.dumps(list(rows), ensure_ascii=False, indent=2)


def render_csv(rows: Sequence[Row], columns: Sequence[Column]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow([header for _, header in columns])
    for row in rows:
        writer.writerow([_stringify(row.get(key)) for key, _ in columns])
    return buffer.getvalue().rstrip("\n")


def render_markdown(rows: Sequence[Row], columns: Sequence[Column]) -> str:
    header = "| " + " | ".join(header for _, header in columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, divider]
    for row in rows:
        cells = [_stringify(row.get(key)).replace("|", "\\|").replace("\n", " ") for key, _ in columns]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render_table(
    rows: Sequence[Row],
    columns: Sequence[Column],
    max_width: int = 48,
) -> str:
    """Render an ASCII table aligned by monospace display width."""
    if not rows:
        return "(no rows)"
    matrix: List[List[str]] = []
    widths = [display_width(header) for _, header in columns]
    for row in rows:
        cells = []
        for index, (key, _) in enumerate(columns):
            cell = truncate(_stringify(row.get(key)), max_width)
            cells.append(cell)
            widths[index] = max(widths[index], display_width(cell))
        matrix.append(cells)

    headers = [pad_right(header, widths[i]) for i, (_, header) in enumerate(columns)]
    border = "-+-".join("-" * w for w in widths)
    lines = [" | ".join(headers), border]
    for cells in matrix:
        lines.append(" | ".join(pad_right(cell, widths[i]) for i, cell in enumerate(cells)))
    return "\n".join(lines)


def render(
    rows: Sequence[Row],
    columns: Sequence[Column],
    fmt: str = "table",
) -> str:
    """Dispatch to the renderer identified by ``fmt``."""
    fmt = (fmt or "table").lower()
    if fmt == "json":
        return render_json(rows)
    if fmt == "csv":
        return render_csv(rows, columns)
    if fmt in ("md", "markdown"):
        return render_markdown(rows, columns)
    if fmt == "table":
        return render_table(rows, columns)
    raise ValueError(f"Unsupported output format: {fmt}")
