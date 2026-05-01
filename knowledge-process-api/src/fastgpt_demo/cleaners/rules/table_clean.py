from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class CleanTableRule(CleanRule):
    name = "clean_table"
    description = "清洗 Markdown 表格：移除空行空列、确保表头结构正确"
    default_enabled = False

    _ROW_RE = re.compile(r"^\s*\|(?:[^\n|]*\|)+\s*$", re.MULTILINE)
    _SEP_RE = re.compile(r"^\s*\|(?:[:\-\s]*\|)+\s*$", re.MULTILINE)

    @staticmethod
    def _parse_row(line: str) -> list[str]:
        cells = line.strip().strip("|").split("|")
        return [c.strip() for c in cells]

    @staticmethod
    def _format_row(cells: list[str]) -> str:
        return "| " + " | ".join(cells) + " |"

    @staticmethod
    def _rebuild_separator(col_count: int) -> str:
        return "| " + " | ".join(["---"] * col_count) + " |"

    @staticmethod
    def _find_non_empty_cols(header: list[str], data_rows: list[list[str]]) -> list[int]:
        total_cols = len(header)
        non_empty: list[int] = []
        for i in range(total_cols):
            is_empty = True
            if i < len(header) and header[i].strip():
                is_empty = False
            for row in data_rows:
                if i < len(row) and row[i].strip():
                    is_empty = False
                    break
            if not is_empty:
                non_empty.append(i)
        return non_empty

    def _clean_table_block(self, lines: list[str]) -> str:
        if len(lines) < 2:
            return "\n".join(lines)

        header = self._parse_row(lines[0])
        data_rows = [self._parse_row(line) for line in lines[2:]]

        data_rows = [r for r in data_rows if any(cell.strip() for cell in r)]

        non_empty_cols = self._find_non_empty_cols(header, data_rows)
        if not non_empty_cols:
            return ""

        if len(non_empty_cols) < len(header):
            header = [header[i] if i < len(header) else "" for i in non_empty_cols]
            data_rows = [
                [r[i] if i < len(r) else "" for i in non_empty_cols]
                for r in data_rows
            ]

        result = self._format_row(header) + "\n"
        result += self._rebuild_separator(len(non_empty_cols)) + "\n"
        for row in data_rows:
            result += self._format_row(row) + "\n"
        return result.rstrip("\n")

    def apply(self, text: str, **kwargs) -> str:
        lines = text.split("\n")
        result_parts: list[str] = []
        table_lines: list[str] = []
        in_table = False

        for line in lines:
            is_row = bool(self._ROW_RE.match(line))
            is_sep = bool(self._SEP_RE.match(line))

            if is_row:
                if not in_table:
                    in_table = True
                    table_lines = [line]
                elif is_sep and len(table_lines) == 1:
                    table_lines.append(line)
                else:
                    table_lines.append(line)
            else:
                if in_table:
                    cleaned = self._clean_table_block(table_lines)
                    if cleaned:
                        result_parts.append(cleaned)
                    table_lines = []
                    in_table = False
                result_parts.append(line)

        if in_table and table_lines:
            cleaned = self._clean_table_block(table_lines)
            if cleaned:
                result_parts.append(cleaned)

        return "\n".join(result_parts)


register(CleanTableRule())
