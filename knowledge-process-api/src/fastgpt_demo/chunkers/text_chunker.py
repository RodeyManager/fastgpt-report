"""
兼容层：保留原有的 split_text_2_chunks 函数签名，内部委托给 RecursiveChunkStrategy。

旧代码可直接继续导入本模块，无需修改。
"""

from __future__ import annotations

from typing import List, Optional

from .recursive_chunker import split_text_2_chunks as _original_split
from .base import SplitResponse

__all__ = ["split_text_2_chunks"]


def split_text_2_chunks(
    text: str,
    chunk_size: int,
    overlap_ratio: float = 0.15,
    paragraph_chunk_deep: int = 5,
    paragraph_chunk_min_size: int = 100,
    max_size: int = 8000,
    custom_reg: Optional[List[str]] = None,
) -> SplitResponse:
    """
    将文本分块（兼容层）。

    所有参数与行为与原函数保持一致，内部实际调用 recursive_chunker 中的实现。
    """
    return _original_split(
        text=text,
        chunk_size=chunk_size,
        overlap_ratio=overlap_ratio,
        paragraph_chunk_deep=paragraph_chunk_deep,
        paragraph_chunk_min_size=paragraph_chunk_min_size,
        max_size=max_size,
        custom_reg=custom_reg,
    )
