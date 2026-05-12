"""
语义分块策略 —— 优先通过 Ollama 调用本地 Embedding 模型计算句子相似度，
在话题转换处切分，保证每个块内部话题高度一致。

降级链路：Ollama Embedding → TF-IDF + 余弦相似度 → Jaccard 词汇重叠率。
"""

from __future__ import annotations

import os
import re
from typing import List

import httpx

from .base import ChunkStrategy, SplitResponse

# 句子结束符：中文 + 英文
_SENTENCE_END_RE = re.compile(r"([。！？；.!?;]+\s*)")

# Ollama 配置：通过环境变量指定地址与模型，默认本地 qwen3-embedding:4b
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "qwen3-embedding:4b")

# 尝试导入 sklearn；若缺失则标记为不可用
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False


def _split_sentences(text: str) -> List[str]:
    """将文本拆分为句子列表，保留结束符。"""
    parts = _SENTENCE_END_RE.split(text)
    sentences: List[str] = []
    i = 0
    while i < len(parts):
        # 偶数索引为句子主体，奇数索引为结束符
        body = parts[i]
        i += 1
        end = parts[i] if i < len(parts) else ""
        i += 1
        sentence = (body + end).strip()
        if sentence:
            sentences.append(sentence)
    return sentences


def _jaccard_similarity(a: str, b: str) -> float:
    """计算两个字符串的词汇 Jaccard 相似度（轻量 fallback）。"""
    set_a = set(re.findall(r"[\u4e00-\u9fa5]|[a-zA-Z]+", a))
    set_b = set(re.findall(r"[\u4e00-\u9fa5]|[a-zA-Z]+", b))
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0.0


def _cosine_similarity_dense(a: List[float], b: List[float]) -> float:
    """计算两个稠密向量的余弦相似度（纯 Python，避免 numpy 依赖）。"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _get_ollama_embeddings(texts: List[str]) -> List[List[float]] | None:
    """
    调用本地 Ollama /api/embed 接口批量获取文本嵌入向量。
    返回 None 表示调用失败，应由上层降级处理。
    """
    if not texts:
        return []
    url = f"{OLLAMA_HOST}/api/embed"
    payload = {"model": OLLAMA_MODEL, "input": texts}
    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            embeddings = data.get("embeddings")
            if isinstance(embeddings, list) and len(embeddings) == len(texts):
                return embeddings
    except Exception:
        pass
    return None


class SemanticChunkStrategy(ChunkStrategy):
    """
    语义分块器。

    优先通过 Ollama 调用本地 Embedding 模型（默认 qwen3-embedding:4b）
    计算相邻句子的语义相似度；若 Ollama 不可用则回退到 TF-IDF / Jaccard。

    参数:
        chunk_size: 目标块长度（字符数），若当前块超过此长度则强制切分。
        semantic_threshold: 相似度阈值（0.0 ~ 1.0）。
                            使用 Embedding 时建议 0.70~0.85；
                            使用 TF-IDF / Jaccard 时建议 0.30~0.50。
                            相邻句子相似度低于此值时产生新块。
        overlap_ratio: 切分后向后一块传递的重叠比例（默认 0.0）。
    """

    def split(
        self,
        text: str,
        chunk_size: int = 500,
        semantic_threshold: float = 0.75,
        overlap_ratio: float = 0.0,
        **kwargs,
    ) -> SplitResponse:
        text = (text or "").strip()
        if not text:
            return {"chunks": [], "chars": 0}

        sentences = _split_sentences(text)
        if not sentences:
            return {"chunks": [text], "chars": len(text)}

        # 单句直接返回
        if len(sentences) == 1:
            return {"chunks": sentences, "chars": len(sentences[0])}

        # 计算相邻句子相似度
        similarities = self._compute_similarities(sentences)

        overlap_len = int(chunk_size * overlap_ratio) if overlap_ratio else 0
        chunks: List[str] = []
        current_chunk = sentences[0]

        for i in range(1, len(sentences)):
            sim = similarities[i - 1]
            next_sentence = sentences[i]

            # 强制切分条件 1：当前块长度已达上限
            force_split = len(current_chunk) >= chunk_size
            # 强制切分条件 2：语义断裂（相似度低于阈值）
            semantic_split = sim < semantic_threshold

            if force_split or semantic_split:
                chunks.append(current_chunk)
                # 构造重叠：若启用 overlap，从当前块尾部取若干句子
                if overlap_len and len(current_chunk) > overlap_len:
                    overlap_text = self._extract_tail(current_chunk, overlap_len)
                    current_chunk = overlap_text + next_sentence
                else:
                    current_chunk = next_sentence
            else:
                current_chunk += next_sentence

        if current_chunk.strip():
            chunks.append(current_chunk)

        return {"chunks": chunks, "chars": sum(len(c) for c in chunks)}

    def _compute_similarities(self, sentences: List[str]) -> List[float]:
        """计算相邻句子的相似度列表，长度 = len(sentences) - 1。"""
        # 优先级 1：Ollama 本地 Embedding（qwen3-embedding:4b）
        embeddings = _get_ollama_embeddings(sentences)
        if embeddings and len(embeddings) == len(sentences):
            return [
                _cosine_similarity_dense(embeddings[i], embeddings[i + 1])
                for i in range(len(sentences) - 1)
            ]

        # 优先级 2：TF-IDF + 余弦相似度
        if _SKLEARN_AVAILABLE and len(sentences) >= 2:
            try:
                vectorizer = TfidfVectorizer()
                tfidf_matrix = vectorizer.fit_transform(sentences)
                sims = []
                for i in range(len(sentences) - 1):
                    vec_i = tfidf_matrix[i : i + 1]
                    vec_j = tfidf_matrix[i + 1 : i + 2]
                    sim = cosine_similarity(vec_i, vec_j)[0][0]
                    sims.append(float(sim))
                return sims
            except Exception:
                pass  # 降级到 fallback

        # 优先级 3：Jaccard 词汇重叠率
        return [_jaccard_similarity(sentences[i], sentences[i + 1]) for i in range(len(sentences) - 1)]

    def _extract_tail(self, text: str, max_len: int) -> str:
        """从文本尾部提取不超过 max_len 字符的片段作为重叠。"""
        if len(text) <= max_len:
            return text
        # 优先在句子边界切分
        idx = max(0, len(text) - max_len)
        # 向后找到最近的句子结束符
        next_end = text.find("\n", idx)
        if next_end == -1:
            next_end = text.find("。", idx)
        if next_end == -1:
            next_end = text.find(". ", idx)
        if next_end != -1:
            return text[next_end + 1 :]
        return text[idx:]
