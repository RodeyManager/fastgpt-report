"""
OpenDataLoader-PDF 解析器
通过 HTTP 调用本地 Docling Server (http://localhost:5002) 解析 PDF
"""

from __future__ import annotations

import httpx

from ._types import ParseResult

DOCLING_SERVER_URL = "http://localhost:5002"
DOCLING_CONVERT_URL = f"{DOCLING_SERVER_URL}/v1/convert/file"


def _extract_texts(doc_json: dict) -> str:
    """从 DoclingDocument JSON 中提取文本，按页组织"""
    texts = doc_json.get("texts", [])
    texts_by_page: dict[int, list[str]] = {}
    for item in texts:
        prov_list = item.get("prov", [])
        if not prov_list:
            continue
        page_no = prov_list[0].get("page_no", 0)
        text = item.get("text", "")
        if not text:
            continue
        texts_by_page.setdefault(page_no, []).append(text)

    pages = []
    for page_no in sorted(texts_by_page.keys()):
        page_lines = texts_by_page[page_no]
        pages.append("\n".join(page_lines))

    return "\n\n".join(pages)


def _extract_tables_as_markdown(doc_json: dict) -> str:
    """将 DoclingDocument 中的表格转为 Markdown"""
    tables = doc_json.get("tables", [])
    if not tables:
        return ""

    md_tables = []
    for table in tables:
        data = table.get("data", [])
        if not data:
            continue
        num_cols = max(len(row) for row in data) if data else 0
        if num_cols == 0:
            continue

        grid = []
        for row in data:
            grid_row = []
            for cell in row:
                cell_text = cell.get("text", "")
                grid_row.append(cell_text)
            grid.append(grid_row)

        if not grid:
            continue

        lines = []
        header = grid[0]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        for row in grid[1:]:
            padded = (row + [""] * len(header))[:len(header)]
            lines.append("| " + " | ".join(padded) + " |")

        md_tables.append("\n".join(lines))

    return "\n\n".join(md_tables)


def parse_opendataloader_pdf(
    buffer: bytes,
    timeout: float = 120.0,
) -> ParseResult:
    """通过 Docling Server 解析 PDF

    参数:
        buffer: PDF 文件字节内容
        timeout: HTTP 请求超时秒数

    返回:
        ParseResult: raw_text 为提取的纯文本，format_text 为含 Markdown 表格的文本
    """
    resp = httpx.post(
        DOCLING_CONVERT_URL,
        files={"files": ("input.pdf", buffer, "application/pdf")},
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()

    errors = data.get("errors", [])
    if errors:
        raise RuntimeError(f"Docling 解析错误: {errors[0]}")

    doc_json = data["document"]["json_content"]

    text_content = _extract_texts(doc_json)
    table_content = _extract_tables_as_markdown(doc_json)

    if table_content:
        format_text = text_content + "\n\n" + table_content
    else:
        format_text = text_content

    raw_text = text_content

    return ParseResult(
        raw_text=raw_text,
        format_text=format_text,
        html_preview="",
        image_list=[],
    )
