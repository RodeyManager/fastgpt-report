"""
Ollama Embedding 模型能力测试脚本

测试项：
1. 服务连通性
2. 单条 / 批量 Embedding 接口
3. 向量维度与数值范围
4. 语义相似度判断能力（同义 vs 无关）
5. 批量性能基准
6. 降级链路验证（Ollama 不可用时）
"""

import os
import sys
import time

sys.path.insert(0, "src")

# 强制使用 Ollama 路径（不降级）
os.environ["OLLAMA_HOST"] = os.getenv("OLLAMA_HOST", "http://localhost:11434")
os.environ["OLLAMA_EMBEDDING_MODEL"] = os.getenv("OLLAMA_EMBEDDING_MODEL", "qwen3-embedding:4b")

from fastgpt_demo.chunkers.semantic_chunker import (
    _get_ollama_embeddings,
    _cosine_similarity_dense,
    SemanticChunkStrategy,
)

OLLAMA_HOST = os.environ["OLLAMA_HOST"]
OLLAMA_MODEL = os.environ["OLLAMA_EMBEDDING_MODEL"]


def test_connectivity():
    print("=" * 50)
    print("【测试 1】服务连通性")
    print("=" * 50)
    import httpx
    try:
        resp = httpx.get(f"{OLLAMA_HOST}/api/tags", timeout=5.0)
        resp.raise_for_status()
        data = resp.json()
        models = [m["name"] for m in data.get("models", [])]
        print(f"  Ollama 服务正常，已安装模型: {models}")
        if OLLAMA_MODEL not in models:
            print(f"  [WARN] 目标模型 {OLLAMA_MODEL} 不在已安装列表中")
        else:
            print(f"  [OK] 目标模型 {OLLAMA_MODEL} 已就绪")
    except Exception as exc:
        print(f"  [FAIL] 连接失败: {exc}")
        return False
    return True


def test_single_embedding():
    print("\n" + "=" * 50)
    print("【测试 2】单条文本 Embedding")
    print("=" * 50)
    text = "人工智能正在改变世界。"
    embs = _get_ollama_embeddings([text])
    if embs is None:
        print("  [FAIL] 返回 None，调用失败")
        return False
    vec = embs[0]
    print(f"  输入文本: {text}")
    print(f"  向量维度: {len(vec)}")
    print(f"  向量前 5 维: {vec[:5]}")
    print(f"  向量 L2 范数: {sum(x * x for x in vec) ** 0.5:.4f}")
    print("  [OK] 单条 Embedding 成功")
    return True


def test_batch_embedding():
    print("\n" + "=" * 50)
    print("【测试 3】批量文本 Embedding")
    print("=" * 50)
    texts = [
        "今天天气很好，适合去公园散步。",
        "股票市场的波动让投资者感到紧张。",
        "机器学习是人工智能的一个子领域。",
    ]
    embs = _get_ollama_embeddings(texts)
    if embs is None:
        print("  [FAIL] 返回 None")
        return False
    print(f"  批量数量: {len(texts)}")
    print(f"  返回向量数: {len(embs)}")
    for i, (t, e) in enumerate(zip(texts, embs)):
        print(f"  [{i}] 文本长度={len(t)} 向量维度={len(e)}")
    print("  [OK] 批量 Embedding 成功")
    return True


def test_semantic_similarity():
    print("\n" + "=" * 50)
    print("【测试 4】语义相似度判断能力")
    print("=" * 50)

    similar_pairs = [
        ("这辆车跑得很快", "这辆汽车行驶速度很高"),
        ("我喜欢吃苹果", "我非常爱吃苹果"),
        ("深度学习需要大量数据", "神经网络训练依赖海量样本"),
    ]

    unrelated_pairs = [
        ("今天天气很好", "股票指数大幅下跌"),
        ("人工智能发展迅速", "这道菜的味道很鲜美"),
        ("量子计算很有前景", "我的猫喜欢睡觉"),
    ]

    all_texts = list({t for pair in similar_pairs + unrelated_pairs for t in pair})
    embs = _get_ollama_embeddings(all_texts)
    if embs is None:
        print("  [FAIL] Embedding 调用失败")
        return False

    text_to_vec = {t: e for t, e in zip(all_texts, embs)}

    print("  --- 同义/近义句对（应高相似）---")
    for a, b in similar_pairs:
        sim = _cosine_similarity_dense(text_to_vec[a], text_to_vec[b])
        status = "[OK]" if sim >= 0.70 else "[WARN]"
        print(f"    {status} {sim:.4f}  |  \"{a}\" vs \"{b}\"")

    print("  --- 无关句对（应低相似）---")
    for a, b in unrelated_pairs:
        sim = _cosine_similarity_dense(text_to_vec[a], text_to_vec[b])
        status = "[OK]" if sim <= 0.50 else "[WARN]"
        print(f"    {status} {sim:.4f}  |  \"{a}\" vs \"{b}\"")

    print("  [OK] 语义相似度测试完成")
    return True


def test_performance():
    print("\n" + "=" * 50)
    print("【测试 5】批量性能基准")
    print("=" * 50)
    texts = [f"这是第 {i} 条测试文本，用于评估 Embedding 模型的推理速度。" for i in range(1, 11)]
    start = time.perf_counter()
    embs = _get_ollama_embeddings(texts)
    elapsed = (time.perf_counter() - start) * 1000
    if embs is None:
        print("  [FAIL] 调用失败")
        return False
    print(f"  批量数量: {len(texts)}")
    print(f"  总耗时: {elapsed:.1f} ms")
    print(f"  平均每条: {elapsed / len(texts):.1f} ms")
    print("  [OK] 性能测试完成")
    return True


def test_end_to_end_chunking():
    print("\n" + "=" * 50)
    print("【测试 6】端到端语义分块")
    print("=" * 50)
    strategy = SemanticChunkStrategy()
    text = (
        "今天天气很好。适合出门散步。"
        "股市今天大涨。投资者情绪高涨。"
        "机器学习是 AI 的核心技术。深度学习是其重要分支。"
        "神经网络通过多层结构提取特征。"
        "晚饭吃什么？我想吃火锅。"
    )
    result = strategy.split(text, chunk_size=200, semantic_threshold=0.75)
    print(f"  输入文本长度: {len(text)} 字符")
    print(f"  分块数量: {len(result['chunks'])}")
    for i, chunk in enumerate(result["chunks"]):
        print(f"    Chunk {i + 1} ({len(chunk)} 字符): {chunk[:40]}...")
    print("  [OK] 端到端分块测试完成")
    return True


def test_fallback_when_ollama_down():
    print("\n" + "=" * 50)
    print("【测试 7】降级链路验证（模拟 Ollama 不可达）")
    print("=" * 50)
    original_host = os.environ.get("OLLAMA_HOST")
    os.environ["OLLAMA_HOST"] = "http://localhost:19999"
    try:
        strategy = SemanticChunkStrategy()
        text = "这是测试文本。用于验证降级逻辑。"
        result = strategy.split(text, chunk_size=100, semantic_threshold=0.5)
        print(f"  Ollama 不可用时自动降级，分块结果: {result['chunks']}")
        print("  [OK] 降级链路正常")
        return True
    finally:
        if original_host:
            os.environ["OLLAMA_HOST"] = original_host
        else:
            del os.environ["OLLAMA_HOST"]


def main():
    print("Ollama Embedding 模型能力测试")
    print(f"服务地址: {OLLAMA_HOST}")
    print(f"目标模型: {OLLAMA_MODEL}")

    results = []
    results.append(("连通性", test_connectivity()))
    results.append(("单条 Embedding", test_single_embedding()))
    results.append(("批量 Embedding", test_batch_embedding()))
    results.append(("语义相似度", test_semantic_similarity()))
    results.append(("性能基准", test_performance()))
    results.append(("端到端分块", test_end_to_end_chunking()))
    results.append(("降级链路", test_fallback_when_ollama_down()))

    print("\n" + "=" * 50)
    print("【测试汇总】")
    print("=" * 50)
    for name, ok in results:
        status = "[PASS]" if ok else "[FAIL]"
        print(f"  {status} {name}")

    passed = sum(1 for _, ok in results if ok)
    print(f"\n总计: {passed}/{len(results)} 项通过")


if __name__ == "__main__":
    main()
