"""
分块策略模块入口。

导出策略注册表、所有策略常量以及向后兼容的 split_text_2_chunks。
"""

from .base import ChunkStrategy, SplitResponse
from .registry import ChunkRegistry, STRATEGY_NAMES
from .recursive_chunker import RecursiveChunkStrategy
from .fixed_chunker import FixedChunkStrategy
from .sliding_window_chunker import SlidingWindowChunkStrategy
from .structure_chunker import StructureChunkStrategy
from .semantic_chunker import SemanticChunkStrategy
from .text_chunker import split_text_2_chunks

__all__ = [
    "ChunkStrategy",
    "SplitResponse",
    "ChunkRegistry",
    "STRATEGY_NAMES",
    "RecursiveChunkStrategy",
    "FixedChunkStrategy",
    "SlidingWindowChunkStrategy",
    "StructureChunkStrategy",
    "SemanticChunkStrategy",
    "split_text_2_chunks",
]
