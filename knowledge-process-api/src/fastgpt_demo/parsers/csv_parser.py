"""CSV parser — reads with stdlib csv, builds Markdown table."""

from __future__ import annotations

import csv
from io import StringIO

from ._types import ParseResult


def parse(buffer: bytes, **kwargs) -> ParseResult:
    """Parse a CSV buffer into raw text + Markdown table."""

    text_content = buffer.decode("utf-8-sig")

    reader = csv.reader(StringIO(text_content))
    rows: list[list[str]] = list(reader)

    raw_text = text_content

    if not rows:
        return ParseResult(
            raw_text=raw_text,
            format_text="",
            html_preview="",
            image_list=[],
        )

    header = rows[0]

    def _sanitize_cell(cell: str) -> str:
        return cell.replace("\n", "\\n")

    sanitized_header = [_sanitize_cell(col) for col in header]
    md_lines: list[str] = [
        f"| {' | '.join(sanitized_header)} |",
        f"| {' | '.join(['---'] * len(header))} |",
    ]

    for row in rows[1:]:
        padded = (row + [""] * len(header))[: len(header)]
        sanitized = [_sanitize_cell(cell) for cell in padded]
        md_lines.append(f"| {' | '.join(sanitized)} |")

    format_text = "\n".join(md_lines)

    html_lines: list[str] = ["<table>"]
    html_lines.append("<thead><tr>")
    for col in header:
        html_lines.append(f"<th>{col}</th>")
    html_lines.append("</tr></thead>")
    html_lines.append("<tbody>")
    for row in rows[1:]:
        padded = (row + [""] * len(header))[: len(header)]
        html_lines.append("<tr>")
        for cell in padded:
            html_lines.append(f"<td>{cell}</td>")
        html_lines.append("</tr>")
    html_lines.append("</tbody></table>")
    html_preview = "\n".join(html_lines)

    return ParseResult(
        raw_text=raw_text,
        format_text=format_text,
        html_preview=html_preview,
        image_list=[],
    )
