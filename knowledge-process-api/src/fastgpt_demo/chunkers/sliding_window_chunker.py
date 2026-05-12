"""
滑动窗口分块策略 —— 按固定窗口大小滑动切割，相邻块之间有重叠。

通过 overlap_ratio 控制重叠长度，可保证切分边界处的上下文不被完全切断。
"""

from __future__ import annotations

from .base import ChunkStrategy, SplitResponse


class SlidingWindowChunkStrategy(ChunkStrategy):
    """
    滑动窗口分块器。

    参数:
        chunk_size: 每个窗口的字符长度。
        overlap_ratio: 相邻窗口的重叠比例（0.0 ~ 1.0）。
                       实际步长 = chunk_size - int(chunk_size * overlap_ratio)。
    """

    def split(
        self,
        text: str,
        chunk_size: int = 500,
        overlap_ratio: float = 0.2,
        **kwargs,
    ) -> SplitResponse:
        text = (text or "").strip()
        if not text:
            return {"chunks": [], "chars": 0}

        overlap_len = int(chunk_size * overlap_ratio)
        step = max(1, chunk_size - overlap_len)

        chunks = []
        i = 0
        while i < len(text):
            chunk = text[i : i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
            i += step

        return {"chunks": chunks, "chars": sum(len(c) for c in chunks)}
