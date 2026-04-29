"""
Markdown conversion module - Python port of FastGPT's markdown conversion utilities.

Provides HTML-to-Markdown conversion and text cleaning functions that match
FastGPT's JavaScript behavior exactly.
"""

from __future__ import annotations

import re
import time

from markdownify import MarkdownConverter, markdownify as md


# ---------------------------------------------------------------------------
# Custom markdownify converter with FastGPT-specific tag handling
# ---------------------------------------------------------------------------


class _FastGPTConverter(MarkdownConverter):
    """Custom markdownify converter matching FastGPT's turndown configuration."""

    def convert_del(self, el, text, parent_aside):
        return f"~~{text}~~"

    def convert_s(self, el, text, parent_aside):
        return f"~~{text}~~"

    def convert_video(self, el, text, parent_aside):
        src = el.get("src", "")
        if src:
            return f"[{src}]({src})"
        # Fall back to <source> child
        source = el.find("source")
        if source is not None:
            s = source.get("src", "")
            return f"[{s}]({s})" if s else ""
        return ""

    def convert_source(self, el, text, parent_aside):
        src = el.get("src", "")
        return f"[{src}]({src})" if src else ""

    def convert_audio(self, el, text, parent_aside):
        src = el.get("src", "")
        return f"[{src}]({src})" if src else ""


# ---------------------------------------------------------------------------
# Core text-cleaning primitives
# ---------------------------------------------------------------------------


def fastgpt_simple_text(text: str = "") -> str:
    """
    Exact port of FastGPT's ``fastGPTSimpleText``.

    Cleans text by removing excess whitespace between Chinese characters,
    normalising line endings, collapsing runs of newlines / whitespace,
    and stripping control characters.
    """
    text = text.strip()

    # Remove spaces between Chinese characters (preserve newlines)
    # JS: /([\u4e00-\u9fa5])[\s&&[^\n]]+([\u4e00-\u9fa5])/g
    # Python: [^\S\n] matches whitespace that is NOT a newline
    text = re.sub(r"([\u4e00-\u9fa5])[^\S\n]+([\u4e00-\u9fa5])", r"\1\2", text)

    # Normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse 3+ consecutive newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse 2+ consecutive whitespace (not newlines) to single space
    text = re.sub(r"[^\S\n]{2,}", " ", text)

    # Replace control chars 0x00-0x08 with space
    text = re.sub(r"[\x00-\x08]", " ", text)

    return text


# Regex to detect characters that markdownify might backslash-escape
_UNESCAPE_PATTERN = re.compile(r"\\([#`!*()+\-\_[\]{}\\.])")


def simple_markdown_text(raw_text: str) -> str:
    """
    Exact port of FastGPT's ``simpleMarkdownText``.

    Post-processes markdown text produced by the converter: cleans link
    formatting, removes unnecessary backslash escapes, normalises literal
    ``\\n`` sequences, and strips leading whitespace before markdown
    structural elements.
    """
    # Step 1 – run the base cleaner first
    raw_text = fastgpt_simple_text(raw_text)

    # Step 2 – clean markdown links: remove newlines in link text
    # JS: rawText.replace(/\[([^\]]+)\]\((.+?)\)/g, ...)
    def _clean_link(m: re.Match) -> str:
        link_text = m.group(1).replace("\n", "")
        url = m.group(2)
        if not url:
            return link_text
        return f"[{link_text}]({url})"

    raw_text = re.sub(r"\[([^\]]+)\]\((.+?)\)", _clean_link, raw_text)

    # Step 3 – remove unnecessary backslash escapes
    # JS guard: only apply when the regex actually matches
    if _UNESCAPE_PATTERN.search(raw_text):
        raw_text = _UNESCAPE_PATTERN.sub(r"\1", raw_text)

    # Step 4 – replace literal \\n with real newline
    raw_text = raw_text.replace("\\\\n", "\n")

    # Step 5 – remove leading spaces before MD structural elements
    # For each pattern, test if \n\s*{pattern} exists, then strip leading spaces
    for pattern in ["####", "###", "##", "#", "```", "~~~"]:
        if re.search(r"\n\s*" + re.escape(pattern), raw_text):
            raw_text = re.sub(
                r"\n( *)(" + re.escape(pattern) + r")",
                r"\n\2",
                raw_text,
            )

    return raw_text.strip()


# ---------------------------------------------------------------------------
# Interactive cleaning with toggle options (used in UI)
# ---------------------------------------------------------------------------

_DEFAULT_OPTIONS = {
    "trim": True,
    "remove_chinese_space": True,
    "normalize_newline": True,
    "collapse_whitespace": True,
    "remove_empty_lines": True,
}


def simple_text(text: str, options: dict | None = None) -> str:
    """
    Interactive text cleaning with individual toggle options.

    Mirrors FastGPT's ``simpleText`` UI helper.  Each option is applied
    independently; control characters (0x00-0x08) are always replaced at
    the end.
    """
    opts: dict = {**_DEFAULT_OPTIONS, **(options or {})}

    if opts.get("trim", True):
        text = text.strip()

    if opts.get("remove_chinese_space", True):
        # Remove spaces between Chinese characters (preserve newlines)
        text = re.sub(r"([\u4e00-\u9fa5])[^\S\n]+([\u4e00-\u9fa5])", r"\1\2", text)

    if opts.get("normalize_newline", True):
        text = text.replace("\r\n", "\n").replace("\r", "\n")

    if opts.get("collapse_whitespace", True):
        text = re.sub(r"[^\S\n]{2,}", " ", text)

    if opts.get("remove_empty_lines", True):
        text = re.sub(r"\n{3,}", "\n\n", text)

    # Always replace control chars at end
    text = re.sub(r"[\x00-\x08]", " ", text)

    return text


# ---------------------------------------------------------------------------
# HTML → Markdown conversion
# ---------------------------------------------------------------------------

_MDX_OPTS = {
    "heading_style": "atx",       # ATX means # headings
    "bullets": "-",
    "strip": ["i", "script", "iframe", "style"],
}


def html_to_markdown(html: str) -> str:
    """
    Convert an HTML string to Markdown.

    Uses *markdownify* with FastGPT-matching options (ATX headings, ``-``
    bullets, stripped tags) plus custom handling for ``<video>``,
    ``<source>``, ``<audio>``, ``<del>``, and ``<s>`` tags.  The result
    is post-processed through :func:`simple_markdown_text`.
    """
    md_text = md(
        html,
        heading_style="atx",
        bullets="-",
        strip=["i", "script", "iframe", "style"],
        converter=_FastGPTConverter,
    )
    return simple_markdown_text(md_text)


# ---------------------------------------------------------------------------
# Top-level dispatcher
# ---------------------------------------------------------------------------

_DOC_EXTENSIONS = {".docx", ".doc"}
_TABLE_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def convert_to_markdown(
    raw_text: str,
    format_text: str,
    file_ext: str,
) -> tuple[str, str]:
    """
    Route conversion based on *file_ext* and return ``(markdown_text, note)``.

    * *docx* / *doc* → :func:`html_to_markdown` (raw_text is HTML from mammoth)
    * *csv* / *xlsx* / *xls* → *format_text* directly (already a MD table)
    * *md* → *raw_text* as-is
    * *html* → :func:`html_to_markdown`
    * everything else → *raw_text* as-is (no conversion)
    """
    ext = file_ext.lower().lstrip(".")

    if f".{ext}" in _DOC_EXTENSIONS:
        result = html_to_markdown(raw_text)
        return result, "Converted from DOCX/DOC via HTML→Markdown"

    if f".{ext}" in _TABLE_EXTENSIONS:
        return format_text, "Used pre-formatted table markdown"

    if ext == "md":
        return raw_text, "Already markdown"

    if ext == "html":
        result = html_to_markdown(raw_text)
        return result, "Converted HTML→Markdown"

    return raw_text, "No conversion applied"


def convert_to_markdown_multi(
    raw_text: str,
    format_text: str,
    file_ext: str,
    tools: list[str] | None = None,
) -> list[dict]:
    if tools is None:
        tools = ["markdownify"]

    ext = file_ext.lower().lstrip(".")
    results = []

    for tool_name in tools:
        start = time.perf_counter()

        if f".{ext}" in _DOC_EXTENSIONS or ext == "html":
            if tool_name == "markdownify":
                md_text = html_to_markdown(raw_text)
            elif tool_name == "markitdown":
                from .markitdown_converter import html_to_markdown_markitdown
                md_text = html_to_markdown_markitdown(raw_text)
            else:
                md_text = raw_text

            if f".{ext}" in _DOC_EXTENSIONS:
                note = f"Converted from DOCX/DOC via HTML→Markdown using {tool_name}"
            else:
                note = f"Converted HTML→Markdown using {tool_name}"
        elif f".{ext}" in _TABLE_EXTENSIONS:
            md_text = format_text
            note = "Used pre-formatted table markdown"
        elif ext == "md":
            md_text = raw_text
            note = "Already markdown"
        else:
            md_text = raw_text
            note = "No conversion applied"

        elapsed = (time.perf_counter() - start) * 1000

        results.append({
            "tool": tool_name,
            "markdown": md_text,
            "note": note,
            "duration_ms": round(elapsed, 2),
        })

    return results
