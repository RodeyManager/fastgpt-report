"""
前端→后端 保险选项传参联合验证
模拟前端 KnowledgeProcessDemo.vue 的 cleanOptions + profile 调用 /api/clean
验证 5 条保险专用规则的启停控制是否正确
"""
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app import app
from fastapi.testclient import TestClient

client = TestClient(app)

results = []
total = 0
passed = 0
failed = 0


def check(name: str, ok: bool, detail: str = ""):
    global total, passed, failed
    total += 1
    if ok:
        passed += 1
        results.append(f"✅ {name}: {detail}")
    else:
        failed += 1
        results.append(f"❌ {name}: {detail}")


print("=" * 80)
print("前端→后端 保险选项传参联合验证")
print("=" * 80)

# --- 模拟前端 insurance Profile 全量调用 ---
print("\n--- 1. insurance Profile 全量调用 ---")

resp = client.post("/api/clean", json={
    "text": (
        "保单号：P202406010001\n"
        "被保险人：张三\n"
        "第三条 保险责任\n"
        "一、基本保障\n"
        "1. 住院医疗\n"
        "因下列原因造成被保险人身故的，保险人不承\n"
        "担给付保险金的责任。\n"
        "第 l2 条 免责条款\n"
    ),
    "profile": "insurance"
})
assert resp.status_code == 200
cleaned = resp.json()["cleaned"]
print(f"清洗后: {cleaned[:200]}")

check("insurance-条款编号", "[L1]" in cleaned and "[L2]" in cleaned and "[L3]" in cleaned,
      "条款编号附加了 [L1][L2][L3] 标记")
check("insurance-元数据保留", "[META:policy_no]" in cleaned and "[META:insured]" in cleaned,
      "保单号和被保人用 [META:*] 包裹")
check("insurance-跨页合并", "保险人不承担给付保险金的责任。" in cleaned,
      "跨页断行已合并")
check("insurance-OCR修复", "第 12 条" in cleaned,
      "OCR l→1 已修复")
check("insurance-被保人未脱敏", "张三" in cleaned,
      "mask_sensitive 默认关闭，姓名保留")

# --- 模拟前端手动开关各规则 ---
print("\n--- 2. 手动开关各保险规则 ---")

# 关闭条款编号
resp = client.post("/api/clean", json={
    "text": "第三条 保险责任",
    "options": {"normalize_clause_numbering": False}
})
check("开关-条款编号off", "[L" not in resp.json()["cleaned"],
      "normalize_clause_numbering=False → 无标签")

# 关闭元数据保留
resp = client.post("/api/clean", json={
    "text": "保单号：P202406010001",
    "options": {"preserve_policy_meta": False}
})
check("开关-元数据off", "[META:" not in resp.json()["cleaned"],
      "preserve_policy_meta=False → 无标签")

# 关闭跨页合并
resp = client.post("/api/clean", json={
    "text": "保险人不承\n担责任。",
    "options": {"merge_broken_clauses": False}
})
check("开关-合并off", "承\n担" in resp.json()["cleaned"],
      "merge_broken_clauses=False → 保留断行")

# 关闭OCR修复
resp = client.post("/api/clean", json={
    "text": "第 l2 条",
    "options": {"fix_ocr_numbering": False}
})
check("开关-OCRoff", "第 l2 条" in resp.json()["cleaned"],
      "fix_ocr_numbering=False → 不修复")

# --- 测试保险脱敏模式（手动开启 mask_sensitive + insurance_mode） ---
print("\n--- 3. 保险脱敏模式 ---")

resp = client.post("/api/clean", json={
    "text": "保单号：P202406010001，电话13812345678，被保人：张三",
    "options": {"mask_sensitive": True, "insurance_mode": True}
})
cleaned2 = resp.json()["cleaned"]
print(f"脱敏后: {cleaned2}")

check("脱敏-保单号", "P202406010001" not in cleaned2 and "P" in cleaned2 and "001" in cleaned2,
      "保单号脱敏：保留前缀和后缀")
check("脱敏-手机号", "13812345678" not in cleaned2 and "138" in cleaned2 and "5678" in cleaned2,
      "手机号脱敏：保留前3后4")
check("脱敏-姓名", "张三" not in cleaned2,
      "姓名脱敏")

# --- 确认非保险 Profile 不受影响 ---
print("\n--- 4. 非保险 Profile 不启用保险规则 ---")

resp = client.post("/api/clean", json={
    "text": "第三条 保险责任\n保单号：P202406010001",
    "profile": "default"
})
cleaned3 = resp.json()["cleaned"]
check("default-无条款标签", "[L" not in cleaned3, "default Profile 不启用条款编号标签")
check("default-无元数据标签", "[META:" not in cleaned3, "default Profile 不启用元数据标签")

resp = client.post("/api/clean", json={
    "text": "第三条 保险责任\n保单号：P202406010001",
    "profile": "pdf_academic"
})
cleaned4 = resp.json()["cleaned"]
check("academic-无条款标签", "[L" not in cleaned4, "pdf_academic Profile 不启用条款编号标签")

# --- 输出报告 ---
print()
print("-" * 80)
print(f"总计: {total} | 通过: {passed} | 失败: {failed}")
print("-" * 80)

for r in results:
    print(r)

if failed > 0:
    print("\n❌ 存在失败项")
    sys.exit(1)
else:
    print("\n✅ 前端→后端保险选项联合验证全部通过")
    sys.exit(0)
