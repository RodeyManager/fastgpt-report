"""
基于结构的分块策略 —— 根据 Markdown 标题层级或 HTML 标签进行切分。

切分时保留标题/标签作为块的上下文前缀，确保每个块都携带足够的结构信息。
"""

from __future__ import annotations

import re
from typing import List

from .base import ChunkStrategy, SplitResponse

# Markdown 标题正则：匹配行首的 # 到 ######
_MD_HEADER_RE = re.compile(r"^(#{1,6}\s+.+)$", re.MULTILINE)

# HTML 块级标签（按优先级排列）
_HTML_BLOCK_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "div"]


class StructureChunkStrategy(ChunkStrategy):
    """
    结构分块器。

    支持两种 structure_type:
      - "markdown": 按 # 标题层级切分，保留上级标题作为上下文。
      - "html": 按 h1-h6 / section / article / div 等块级标签切分。

    若某一节长度超过 chunk_size，会进一步按段落（\n\n）做二次拆分。
    """

    def split(
        self,
        text: str,
        structure_type: str = "markdown",
        chunk_size: int = 500,
        **kwargs,
    ) -> SplitResponse:
        text = text or ""
        if not text.strip():
            return {"chunks": [], "chars": 0}

        if structure_type == "markdown":
            chunks = self._split_markdown(text, chunk_size)
        elif structure_type == "html":
            chunks = self._split_html(text, chunk_size)
        else:
            raise ValueError(f"不支持的 structure_type: {structure_type}，仅支持 markdown / html")

        return {"chunks": chunks, "chars": sum(len(c) for c in chunks)}

    # ------------------------------------------------------------------
    # Markdown 分块
    # ------------------------------------------------------------------

    def _split_markdown(self, text: str, chunk_size: int) -> List[str]:
        """按 Markdown 标题切分，保留标题上下文。"""
        # 在标题前插入占位符，方便 split
        parts = _MD_HEADER_RE.split(text)
        # split 后奇数索引为标题，偶数索引为内容
        chunks: List[str] = []
        current_header = ""

        i = 0
        while i < len(parts):
            part = parts[i]
            if not part.strip():
                i += 1
                continue

            # 判断当前 part 是否是标题
            if _MD_HEADER_RE.match(part):
                current_header = part.strip()
                i += 1
                # 下一段是内容
                if i < len(parts):
                    content = parts[i]
                    block = f"{current_header}\n{content}"
                    chunks.extend(self._truncate_block(block, chunk_size, current_header))
                i += 1
            else:
                # 无标题的引言段落
                chunks.extend(self._truncate_block(part, chunk_size, ""))
                i += 1

        return [c.strip() for c in chunks if c.strip()]

    def _truncate_block(self, block: str, chunk_size: int, header: str) -> List[str]:
        """若单节过长，按段落二次拆分，并保留标题前缀。"""
        if len(block) <= chunk_size:
            return [block]

        paragraphs = [p for p in block.split("\n\n") if p.strip()]
        result: List[str] = []
        current = header + "\n" if header else ""

        for p in paragraphs:
            candidate = (current + "\n" + p).strip() if current else p.strip()
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    result.append(current)
                current = (header + "\n" + p).strip() if header else p.strip()

        if current:
            result.append(current)
        return result

    # ------------------------------------------------------------------
    # HTML 分块
    # ------------------------------------------------------------------

    def _split_html(self, text: str, chunk_size: int) -> List[str]:
        """按 HTML 块级标签切分。"""
        try:
            from bs4 import BeautifulSoup
        except ImportError as exc:
            raise ImportError(
                "HTML 结构分块需要 beautifulsoup4，请安装: pip install beautifulsoup4"
            ) from exc

        soup = BeautifulSoup(text, "html.parser")
        # 移除 script / style
        for tag in soup(["script", "style"]):
            tag.decompose()

        chunks: List[str] = []
        for tag_name in _HTML_BLOCK_TAGS:
            elements = soup.find_all(tag_name)
            if elements:
                for elem in elements:
                    block = elem.get_text(separator="\n", strip=True)
                    if block:
                        chunks.extend(self._truncate_block(block, chunk_size, ""))
                # 找到最高优先级的标签后即返回，避免重复切分
                break

        # 若未找到任何块级标签，将整个文档视为一块
        if not chunks:
            plain = soup.get_text(separator="\n", strip=True)
            if plain:
                chunks = self._truncate_block(plain, chunk_size, "")

        return [c.strip() for c in chunks if c.strip()]
