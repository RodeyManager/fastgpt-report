"""
分块策略注册表 / 工厂。

通过字符串 key 获取对应的 ChunkStrategy 实例，实现算法切换的统一入口。
"""

from __future__ import annotations

from .base import ChunkStrategy
from .recursive_chunker import RecursiveChunkStrategy
from .fixed_chunker import FixedChunkStrategy
from .sliding_window_chunker import SlidingWindowChunkStrategy
from .structure_chunker import StructureChunkStrategy
from .semantic_chunker import SemanticChunkStrategy

# 策略名称到类的映射
_STRATEGIES: dict[str, type[ChunkStrategy]] = {
    "recursive": RecursiveChunkStrategy,
    "fixed": FixedChunkStrategy,
    "sliding_window": SlidingWindowChunkStrategy,
    "structure": StructureChunkStrategy,
    "semantic": SemanticChunkStrategy,
}

# 对外暴露的合法策略标识（前端可据此渲染下拉选项）
STRATEGY_NAMES = list(_STRATEGIES.keys())


class ChunkRegistry:
    """
    分块策略工厂。

    示例:
        strategy = ChunkRegistry.get("recursive")
        result = strategy.split(text="...", chunk_size=500)
    """

    @staticmethod
    def get(name: str) -> ChunkStrategy:
        """
        根据策略名称获取策略实例。

        参数:
            name: 策略标识，如 "recursive"、"semantic" 等。

        返回:
            ChunkStrategy 实例。

        抛出:
            ValueError: 若 name 不在注册表中。
        """
        name = name.lower().strip()
        cls = _STRATEGIES.get(name)
        if cls is None:
            available = ", ".join(_STRATEGIES.keys())
            raise ValueError(f"未知的分块策略 '{name}'，可用策略: {available}")
        return cls()

    @staticmethod
    def list_strategies() -> list[str]:
        """返回所有已注册的策略名称列表。"""
        return list(_STRATEGIES.keys())
