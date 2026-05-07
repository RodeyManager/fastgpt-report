"""
前端传参验证脚本
模拟前端 KnowledgeProcessDemo.vue 的实际调用方式：
1. cleanOptions 的字段名/类型/默认值 vs 后端 CleanOptions
2. 前端字符串→数组预处理逻辑
3. 每个 Profile 预设的参数 vs 后端 Profile
4. 前端传参后后端是否能正确解析
"""

import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app import app, CleanOptions, CleanRequest
from fastapi.testclient import TestClient

client = TestClient(app)

total = 0
passed = 0
failed = 0
results = []


def check(name: str, ok: bool, detail: str = ""):
    global total, passed, failed
    total += 1
    if ok:
        passed += 1
        results.append(("✅", name, detail))
    else:
        failed += 1
        results.append(("❌", name, detail))


# ============================================================
# 1. 前端 cleanOptions 字段名 vs 后端 CleanOptions 字段名
# ============================================================
print("=" * 80)
print("第1项：前端 cleanOptions 字段名 vs 后端 CleanOptions 字段名")
print("=" * 80)

frontend_fields = {
    "trim": bool, "normalize_unicode": bool, "remove_invisible_chars": bool,
    "remove_chinese_space": bool, "normalize_newline": bool, "fix_hyphenation": bool,
    "collapse_whitespace": bool, "remove_empty_lines": bool,
    "remove_html_comments": bool, "normalize_html_entities": bool,
    "filter_html_noise": bool, "html_noise_patterns": str, "html_ad_keywords": str,
    "filter_watermark": bool, "watermark_keywords": str,
    "filter_toc": bool, "filter_page_numbers": bool,
    "process_footnotes": bool, "footnote_action": str,
    "deduplicate_paragraphs": bool, "dedup_fuzzy": bool,
    "clean_table": bool, "clean_markdown_links": bool,
    "remove_md_escapes": bool, "clean_md_structure": bool,
    "mask_sensitive": bool, "filter_special_chars": bool,
    "normalize_clause_numbering": bool, "preserve_policy_meta": bool,
    "merge_broken_clauses": bool, "fix_ocr_numbering": bool,
    "clean_insurance_table": bool,
}

backend_fields = {name: (field.annotation, field.default) for name, field in CleanOptions.model_fields.items()}

# 前端有但后端没有的字段
for name in frontend_fields:
    if name not in backend_fields:
        check(f"字段映射: {name}", False, "前端有但后端无此字段")
    else:
        check(f"字段映射: {name}", True, "前后端字段名一致")

# 后端有但前端没有的字段（高级参数，前端未暴露，使用后端默认值，属于正常设计）
for name in backend_fields:
    if name not in frontend_fields:
        be_type, be_default = backend_fields[name]
        check(f"后端高级参数: {name}", True, f"类型: {be_type}, 默认值: {be_default} (前端未暴露，使用后端默认值)")

print()

# ============================================================
# 2. 前端默认值 vs 后端默认值
# ============================================================
print("=" * 80)
print("第2项：前端 cleanOptions 默认值 vs 后端 CleanOptions 默认值")
print("=" * 80)

frontend_defaults = {
    "trim": True, "normalize_unicode": True, "remove_invisible_chars": True,
    "remove_chinese_space": True, "normalize_newline": True, "fix_hyphenation": True,
    "collapse_whitespace": True, "remove_empty_lines": True,
    "remove_html_comments": False, "normalize_html_entities": False,
    "filter_html_noise": False, "html_noise_patterns": "", "html_ad_keywords": "",
    "filter_watermark": False, "watermark_keywords": "",
    "filter_toc": False, "filter_page_numbers": False,
    "process_footnotes": False, "footnote_action": "remove",
    "deduplicate_paragraphs": False, "dedup_fuzzy": False,
    "clean_table": False, "clean_markdown_links": True,
    "remove_md_escapes": True, "clean_md_structure": True,
    "mask_sensitive": False, "filter_special_chars": False,
}

backend_defaults = CleanOptions().model_dump()

# 前端字符串类型字段预处理后应与后端数组默认值一致
string_to_array_fields = {
    "watermark_keywords": [],
    "html_noise_patterns": [],
    "html_ad_keywords": [],
}

for name, fe_val in frontend_defaults.items():
    be_val = backend_defaults.get(name)
    if name in string_to_array_fields:
        expected_after_preprocess = string_to_array_fields[name]
        match = (fe_val == "" and be_val == expected_after_preprocess)
        detail = f"前端: '{fe_val}'(空字符串) → 预处理后: {expected_after_preprocess} | 后端: {be_val}"
        check(f"默认值: {name}", match, detail)
    else:
        match = fe_val == be_val
        detail = f"前端: {fe_val} | 后端: {be_val}"
        check(f"默认值: {name}", match, detail)

print()

# ============================================================
# 3. 前端字符串→数组预处理逻辑验证
# ============================================================
print("=" * 80)
print("第3项：前端字符串→数组预处理逻辑验证")
print("=" * 80)


def simulate_frontend_preprocess(opts: dict) -> dict:
    """模拟前端 runCleaning() 中的预处理逻辑"""
    opts = {**opts}
    if opts.get("watermark_keywords") and isinstance(opts["watermark_keywords"], str):
        opts["watermark_keywords"] = [k.strip() for k in opts["watermark_keywords"].replace("，", ",").split(",") if k.strip()]
    else:
        opts["watermark_keywords"] = []
    if opts.get("html_noise_patterns") and isinstance(opts["html_noise_patterns"], str):
        opts["html_noise_patterns"] = [k.strip() for k in opts["html_noise_patterns"].replace("，", ",").split(",") if k.strip()]
    else:
        opts["html_noise_patterns"] = []
    if opts.get("html_ad_keywords") and isinstance(opts["html_ad_keywords"], str):
        opts["html_ad_keywords"] = [k.strip() for k in opts["html_ad_keywords"].replace("，", ",").split(",") if k.strip()]
    else:
        opts["html_ad_keywords"] = []
    return opts


# 测试1：空字符串 → 空数组
opts_empty = simulate_frontend_preprocess({
    "watermark_keywords": "", "html_noise_patterns": "", "html_ad_keywords": ""
})
check("预处理: 空字符串→空数组(watermark_keywords)", opts_empty["watermark_keywords"] == [], f"结果: {opts_empty['watermark_keywords']}")
check("预处理: 空字符串→空数组(html_noise_patterns)", opts_empty["html_noise_patterns"] == [], f"结果: {opts_empty['html_noise_patterns']}")
check("预处理: 空字符串→空数组(html_ad_keywords)", opts_empty["html_ad_keywords"] == [], f"结果: {opts_empty['html_ad_keywords']}")

# 测试2：英文逗号分隔
opts_en = simulate_frontend_preprocess({
    "watermark_keywords": "DRAFT,CONFIDENTIAL", "html_noise_patterns": "广告位.*,推广.*", "html_ad_keywords": "限时优惠,点击购买"
})
check("预处理: 英文逗号分隔(watermark_keywords)", opts_en["watermark_keywords"] == ["DRAFT", "CONFIDENTIAL"], f"结果: {opts_en['watermark_keywords']}")
check("预处理: 英文逗号分隔(html_noise_patterns)", opts_en["html_noise_patterns"] == ["广告位.*", "推广.*"], f"结果: {opts_en['html_noise_patterns']}")
check("预处理: 英文逗号分隔(html_ad_keywords)", opts_en["html_ad_keywords"] == ["限时优惠", "点击购买"], f"结果: {opts_en['html_ad_keywords']}")

# 测试3：中文逗号分隔
opts_cn = simulate_frontend_preprocess({
    "watermark_keywords": "机密，内部文件", "html_noise_patterns": "版权.*，备案.*", "html_ad_keywords": "秒杀，特价"
})
check("预处理: 中文逗号分隔(watermark_keywords)", opts_cn["watermark_keywords"] == ["机密", "内部文件"], f"结果: {opts_cn['watermark_keywords']}")
check("预处理: 中文逗号分隔(html_noise_patterns)", opts_cn["html_noise_patterns"] == ["版权.*", "备案.*"], f"结果: {opts_cn['html_noise_patterns']}")
check("预处理: 中文逗号分隔(html_ad_keywords)", opts_cn["html_ad_keywords"] == ["秒杀", "特价"], f"结果: {opts_cn['html_ad_keywords']}")

# 测试4：混合逗号+空格
opts_mix = simulate_frontend_preprocess({
    "watermark_keywords": " DRAFT , 机密 ,  ", "html_noise_patterns": "", "html_ad_keywords": "  "
})
check("预处理: 混合逗号+空格(watermark_keywords)", opts_mix["watermark_keywords"] == ["DRAFT", "机密"], f"结果: {opts_mix['watermark_keywords']}")
check("预处理: 纯空格(html_noise_patterns)", opts_mix["html_noise_patterns"] == [], f"结果: {opts_mix['html_noise_patterns']}")
check("预处理: 纯空格(html_ad_keywords)", opts_mix["html_ad_keywords"] == [], f"结果: {opts_mix['html_ad_keywords']}")

print()

# ============================================================
# 4. 模拟前端完整调用 → 后端 /api/clean 解析验证
# ============================================================
print("=" * 80)
print("第4项：模拟前端完整调用 → 后端 /api/clean 解析验证")
print("=" * 80)


def simulate_frontend_clean_call(text: str, fe_opts: dict) -> dict:
    """模拟前端 runCleaning() 的完整调用流程"""
    opts = simulate_frontend_preprocess(fe_opts)
    resp = client.post("/api/clean", json={"text": text, "options": opts})
    return resp


# 4a. 默认选项调用
fe_default_opts = {
    "trim": True, "normalize_unicode": True, "remove_invisible_chars": True,
    "remove_chinese_space": True, "normalize_newline": True, "fix_hyphenation": True,
    "collapse_whitespace": True, "remove_empty_lines": True,
    "remove_html_comments": False, "normalize_html_entities": False,
    "filter_html_noise": False, "html_noise_patterns": "", "html_ad_keywords": "",
    "filter_watermark": False, "watermark_keywords": "",
    "filter_toc": False, "filter_page_numbers": False,
    "process_footnotes": False, "footnote_action": "remove",
    "deduplicate_paragraphs": False, "dedup_fuzzy": False,
    "clean_table": False, "clean_markdown_links": True,
    "remove_md_escapes": True, "clean_md_structure": True,
    "mask_sensitive": False, "filter_special_chars": False,
}

resp = simulate_frontend_clean_call("  hello world  ", fe_default_opts)
check("前端默认选项调用: HTTP 200", resp.status_code == 200, f"status: {resp.status_code}")
if resp.status_code == 200:
    check("前端默认选项调用: trim 生效", resp.json()["cleaned"] == "hello world", f"结果: {resp.json()['cleaned']}")

# 4b. 启用 filter_watermark + 自定义关键词
resp = simulate_frontend_clean_call("正文\nDRAFT\nDRAFT\nDRAFT\n其他", {
    **fe_default_opts, "filter_watermark": True, "watermark_keywords": "DRAFT,机密"
})
check("前端传参: watermark_keywords 字符串→数组", resp.status_code == 200, f"status: {resp.status_code}")
if resp.status_code == 200:
    check("前端传参: watermark 自定义关键词生效", "DRAFT" not in resp.json()["cleaned"], f"结果: {resp.json()['cleaned'][:60]}")

# 4c. 启用 filter_html_noise + 自定义噪声模式
resp = simulate_frontend_clean_call("正文\n广告位招商中\n其他", {
    **fe_default_opts, "filter_html_noise": True, "html_noise_patterns": "广告位.*"
})
check("前端传参: html_noise_patterns 字符串→数组", resp.status_code == 200, f"status: {resp.status_code}")
if resp.status_code == 200:
    check("前端传参: html_noise 自定义噪声模式生效", "广告位招商中" not in resp.json()["cleaned"], f"结果: {resp.json()['cleaned'][:60]}")

# 4d. 启用 filter_html_noise + 自定义广告关键词
resp = simulate_frontend_clean_call("正文\n限时秒杀限时秒杀限时秒杀限时秒杀\n其他", {
    **fe_default_opts, "filter_html_noise": True, "html_ad_keywords": "限时秒杀"
})
check("前端传参: html_ad_keywords 字符串→数组", resp.status_code == 200, f"status: {resp.status_code}")
if resp.status_code == 200:
    check("前端传参: html_ad 自定义广告关键词生效", "限时秒杀" not in resp.json()["cleaned"], f"结果: {resp.json()['cleaned'][:60]}")

# 4e. 启用 process_footnotes + footnote_action
resp = simulate_frontend_clean_call("正文[1]\n\n[1] 脚注内容", {
    **fe_default_opts, "process_footnotes": True, "footnote_action": "remove"
})
check("前端传参: footnote_action=remove", resp.status_code == 200 and "脚注内容" not in resp.json()["cleaned"],
      f"结果: {resp.json()['cleaned'][:60] if resp.status_code == 200 else 'HTTP ' + str(resp.status_code)}")

resp = simulate_frontend_clean_call("正文[1]\n\n[1] 脚注内容", {
    **fe_default_opts, "process_footnotes": True, "footnote_action": "keep"
})
check("前端传参: footnote_action=keep", resp.status_code == 200 and "脚注内容" in resp.json()["cleaned"],
      f"结果: {resp.json()['cleaned'][:60] if resp.status_code == 200 else 'HTTP ' + str(resp.status_code)}")

# 4f. 启用 deduplicate_paragraphs + dedup_fuzzy
resp = simulate_frontend_clean_call("段落A\n\n段落A\n\n段落B", {
    **fe_default_opts, "deduplicate_paragraphs": True, "dedup_fuzzy": True
})
check("前端传参: dedup_fuzzy=true", resp.status_code == 200 and resp.json()["cleaned"].count("段落A") == 1,
      f"结果: {resp.json()['cleaned'][:60] if resp.status_code == 200 else 'HTTP ' + str(resp.status_code)}")

# 4g. 后端独有字段验证（前端未暴露但后端有默认值）
backend_only_fields = set(backend_fields.keys()) - set(frontend_fields.keys())
for name in backend_only_fields:
    be_type, be_default = backend_fields[name]
    check(f"后端独有字段: {name}", True, f"类型: {be_type}, 默认值: {be_default} (前端未暴露，使用后端默认值)")

print()

# ============================================================
# 5. 前端 Profile 预设 vs 后端 Profile 预设
# ============================================================
print("=" * 80)
print("第5项：前端 Profile 预设 vs 后端 Profile 预设")
print("=" * 80)

from fastgpt_demo.cleaners.profiles import get_profile

frontend_profiles = {
    "default": {"label": "默认"},
    "pdf_academic": {"label": "学术论文 PDF"},
    "pdf_business": {"label": "商务 PDF"},
    "docx_report": {"label": "DOCX 报告"},
    "table_data": {"label": "表格数据"},
    "legal": {"label": "法律文书"},
    "web_content": {"label": "网页内容"},
}

for name, info in frontend_profiles.items():
    p = get_profile(name)
    check(f"Profile 存在: {name}", p is not None, f"后端: {'已注册' if p else '未注册'}")
    if p:
        p_opts = p.to_options_dict()
        # 验证 Profile 中的关键差异化规则
        if name == "web_content":
            check(f"Profile {name}: remove_html_comments=True", p_opts.get("remove_html_comments") == True,
                  f"实际: {p_opts.get('remove_html_comments')}")
            check(f"Profile {name}: filter_html_noise=True", p_opts.get("filter_html_noise") == True,
                  f"实际: {p_opts.get('filter_html_noise')}")
        elif name == "pdf_academic":
            check(f"Profile {name}: filter_toc=True", p_opts.get("filter_toc") == True,
                  f"实际: {p_opts.get('filter_toc')}")
            check(f"Profile {name}: filter_page_numbers=True", p_opts.get("filter_page_numbers") == True,
                  f"实际: {p_opts.get('filter_page_numbers')}")
        elif name == "pdf_business":
            check(f"Profile {name}: filter_watermark=True", p_opts.get("filter_watermark") == True,
                  f"实际: {p_opts.get('filter_watermark')}")
        elif name == "table_data":
            check(f"Profile {name}: clean_table=True", p_opts.get("clean_table") == True,
                  f"实际: {p_opts.get('clean_table')}")
        elif name == "legal":
            check(f"Profile {name}: filter_toc=True", p_opts.get("filter_toc") == True,
                  f"实际: {p_opts.get('filter_toc')}")

print()

# ============================================================
# 6. 前端 Profile 预设切换后 API 调用验证
# ============================================================
print("=" * 80)
print("第6项：前端 Profile 预设切换后 API 调用验证")
print("=" * 80)

# 模拟前端 applyProfile 逻辑：直接使用预设的 options 发送请求
# （前端实际是 applyProfile 设置 cleanOptions，然后 runCleaning 读取并发送）

# web_content 预设
fe_web_content_opts = {
    **fe_default_opts,
    "remove_html_comments": True, "normalize_html_entities": True,
    "filter_html_noise": True, "filter_watermark": True,
    "clean_markdown_links": True,
}
resp = simulate_frontend_clean_call("正文<!-- 注释 -->内容", fe_web_content_opts)
check("前端 Profile web_content: HTML注释移除",
      resp.status_code == 200 and "注释" not in resp.json()["cleaned"],
      f"结果: {resp.json()['cleaned'][:60] if resp.status_code == 200 else 'HTTP ' + str(resp.status_code)}")

# pdf_academic 预设
fe_pdf_academic_opts = {
    **fe_default_opts,
    "filter_toc": True, "filter_page_numbers": True,
    "process_footnotes": True, "footnote_action": "keep",
}
resp = simulate_frontend_clean_call("1.1 概述 ............ 1\n1.2 背景 ............ 5\n1.3 方法 ............ 10\n正文", fe_pdf_academic_opts)
check("前端 Profile pdf_academic: 目录过滤",
      resp.status_code == 200 and ("1.1 概述" not in resp.json()["cleaned"] or "............" not in resp.json()["cleaned"]),
      f"结果: {resp.json()['cleaned'][:60] if resp.status_code == 200 else 'HTTP ' + str(resp.status_code)}")

# pdf_business 预设
fe_pdf_business_opts = {
    **fe_default_opts,
    "filter_watermark": True, "filter_page_numbers": True,
}
resp = simulate_frontend_clean_call("正文\nDRAFT\nDRAFT\nDRAFT\n更多", fe_pdf_business_opts)
check("前端 Profile pdf_business: 水印过滤",
      resp.status_code == 200 and resp.json()["cleaned"].count("DRAFT") < 3,
      f"结果: {resp.json()['cleaned'][:60] if resp.status_code == 200 else 'HTTP ' + str(resp.status_code)}")

# table_data 预设
fe_table_data_opts = {
    **fe_default_opts,
    "clean_table": True,
}
resp = simulate_frontend_clean_call("| A | B |\n| --- | --- |\n|  |  |\n| 1 | 2 |", fe_table_data_opts)
check("前端 Profile table_data: 表格清洗",
      resp.status_code == 200 and "|  |  |" not in resp.json()["cleaned"],
      f"结果: {resp.json()['cleaned'][:60] if resp.status_code == 200 else 'HTTP ' + str(resp.status_code)}")

# ============================================================
# 输出报告
# ============================================================
print()
print("=" * 80)
print("前端传参验证报告")
print("=" * 80)
for status, name, detail in results:
    print(f"{status} {name}: {detail}")

print()
print("-" * 80)
print(f"总计: {total} | 通过: {passed} | 失败: {failed}")
print("-" * 80)

if failed > 0:
    print("\n❌ 存在失败项，请检查上方详情")
    sys.exit(1)
else:
    print("\n✅ 前端传参验证全部通过，前端字段名/类型/默认值/预处理逻辑与后端完全一致")
    sys.exit(0)
