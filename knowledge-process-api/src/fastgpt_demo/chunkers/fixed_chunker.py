"""
固定长度分块策略 —— 按固定字符数硬切，无重叠。

适用于对切分边界无语义要求、追求极致速度的场景。
"""

from __future__ import annotations

from .base import ChunkStrategy, SplitResponse


class FixedChunkStrategy(ChunkStrategy):
    """
    固定长度分块器。

    将文本按 chunk_size 字符为一段顺序切割，最后不足长度的部分直接保留。
    切割前会先去除首尾空白；空文本返回空列表。
    """

    def split(self, text: str, chunk_size: int = 500, **kwargs) -> SplitResponse:
        text = (text or "").strip()
        if not text:
            return {"chunks": [], "chars": 0}

        chunks = []
        for i in range(0, len(text), chunk_size):
            chunk = text[i : i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)

        return {"chunks": chunks, "chars": sum(len(c) for c in chunks)}
