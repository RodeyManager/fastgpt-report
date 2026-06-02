"""
分块策略抽象基类与通用类型定义。

所有具体分块策略必须继承 ChunkStrategy 并实现 split 方法，
以保证后端接口对多种算法的统一调用。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List

# 统一的分块响应结构：{ "chunks": ["块1", "块2", ...], "chars": 总字符数 }
SplitResponse = Dict[str, object]


class ChunkStrategy(ABC):
    """分块策略抽象基类。"""

    @abstractmethod
    def split(self, text: str, **kwargs) -> SplitResponse:
        """
        执行文本分块。

        参数:
            text: 待分块的原始文本。
            **kwargs: 各策略所需的专属参数（如 chunk_size、overlap_ratio 等）。

        返回:
            SplitResponse，必须包含 chunks（List[str]）与 chars（int）两个键。
        """
        ...
