"""
全量验证脚本：模拟前端调用 /api/clean，逐条验证每条规则的启用/禁用效果
输出详细的验证报告，包含每条规则的输入、预期输出、实际输出和验证结果
"""

import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app import app
from fastapi.testclient import TestClient

client = TestClient(app)

BASE_OPTS_OFF = {
    "trim": False, "normalize_unicode": False, "remove_invisible_chars": False,
    "remove_chinese_space": False, "normalize_newline": False, "fix_hyphenation": False,
    "collapse_whitespace": False, "remove_empty_lines": False,
    "filter_watermark": False, "watermark_keywords": [], "watermark_min_repeat": 2,
    "watermark_max_line_length": 30,
    "deduplicate_paragraphs": False, "dedup_fuzzy": False, "dedup_fuzzy_threshold": 0.9,
    "clean_table": False, "mask_sensitive": False, "filter_special_chars": False,
    "clean_markdown_links": False, "remove_md_escapes": False, "clean_md_structure": False,
    "filter_toc": False, "filter_page_numbers": False,
    "process_footnotes": False, "footnote_action": "remove",
    "remove_html_comments": False, "normalize_html_entities": False,
    "filter_html_noise": False, "html_noise_patterns": [], "html_ad_keywords": [],
}

results = []
total = 0
passed = 0
failed = 0


def verify(rule_name: str, text: str, opts: dict, check_fn, desc: str):
    global total, passed, failed
    total += 1
    resp = client.post("/api/clean", json={"text": text, "options": opts})
    ok = resp.status_code == 200
    actual = resp.json().get("cleaned", "") if ok else f"HTTP {resp.status_code}"
    rule_ok = False
    detail = ""
    try:
        rule_ok = check_fn(actual)
        detail = "PASS" if rule_ok else "FAIL"
    except Exception as e:
        detail = f"ERROR: {e}"
    if rule_ok:
        passed += 1
    else:
        failed += 1
    results.append({
        "rule": rule_name, "desc": desc, "input": text[:80],
        "actual": actual[:80] if isinstance(actual, str) else str(actual)[:80],
        "result": detail,
    })


def verify_profile(rule_name: str, text: str, profile: str, check_fn, desc: str):
    global total, passed, failed
    total += 1
    resp = client.post("/api/clean", json={"text": text, "profile": profile})
    ok = resp.status_code == 200
    actual = resp.json().get("cleaned", "") if ok else f"HTTP {resp.status_code}"
    rule_ok = False
    detail = ""
    try:
        rule_ok = check_fn(actual)
        detail = "PASS" if rule_ok else "FAIL"
    except Exception as e:
        detail = f"ERROR: {e}"
    if rule_ok:
        passed += 1
    else:
        failed += 1
    results.append({
        "rule": rule_name, "desc": desc, "input": text[:80],
        "actual": actual[:80] if isinstance(actual, str) else str(actual)[:80],
        "result": detail,
    })


# 1. trim
verify("trim", "  hello world  ", {**BASE_OPTS_OFF, "trim": True},
       lambda r: r == "hello world", "启用：去除首尾空白")
verify("trim", "  hello world  ", {**BASE_OPTS_OFF, "trim": False},
       lambda r: r == "  hello world  ", "禁用：保留首尾空白")

# 2. normalize_unicode
verify("normalize_unicode", "Ｈｅｌｌｏ１２３", {**BASE_OPTS_OFF, "normalize_unicode": True},
       lambda r: "Hello123" in r, "启用：全角→半角")
verify("normalize_unicode", "Ｈｅｌｌｏ", {**BASE_OPTS_OFF, "normalize_unicode": False},
       lambda r: "Ｈｅｌｌｏ" in r, "禁用：保留全角")

# 3. remove_invisible_chars
verify("remove_invisible_chars", "hello\u200bworld", {**BASE_OPTS_OFF, "remove_invisible_chars": True},
       lambda r: "\u200b" not in r and "helloworld" in r, "启用：移除零宽空格")
verify("remove_invisible_chars", "hello\u200bworld", {**BASE_OPTS_OFF, "remove_invisible_chars": False},
       lambda r: "\u200b" in r, "禁用：保留零宽空格")

# 4. remove_chinese_space
verify("remove_chinese_space", "你好 世界", {**BASE_OPTS_OFF, "remove_chinese_space": True},
       lambda r: "你好世界" in r, "启用：移除中文间空格")
verify("remove_chinese_space", "你好 世界", {**BASE_OPTS_OFF, "remove_chinese_space": False},
       lambda r: "你好 世界" in r, "禁用：保留中文间空格")

# 5. normalize_newline
verify("normalize_newline", "line1\r\nline2\rline3", {**BASE_OPTS_OFF, "normalize_newline": True},
       lambda r: "\r" not in r, "启用：统一换行符")
verify("normalize_newline", "line1\r\nline2", {**BASE_OPTS_OFF, "normalize_newline": False},
       lambda r: "\r" in r, "禁用：保留原始换行")

# 6. fix_hyphenation
verify("fix_hyphenation", "knowl-\nedge", {**BASE_OPTS_OFF, "fix_hyphenation": True},
       lambda r: "knowledge" in r, "启用：修复断行连字符")
verify("fix_hyphenation", "knowl-\nedge", {**BASE_OPTS_OFF, "fix_hyphenation": False},
       lambda r: "knowl-\nedge" in r, "禁用：保留断行连字符")

# 7. collapse_whitespace
verify("collapse_whitespace", "hello    world", {**BASE_OPTS_OFF, "collapse_whitespace": True},
       lambda r: "    " not in r, "启用：合并连续空白")
verify("collapse_whitespace", "hello    world", {**BASE_OPTS_OFF, "collapse_whitespace": False},
       lambda r: "    " in r, "禁用：保留连续空白")

# 8. remove_empty_lines
verify("remove_empty_lines", "line1\n\n\n\nline2", {**BASE_OPTS_OFF, "remove_empty_lines": True},
       lambda r: r.count("\n") <= 2, "启用：压缩空行")
verify("remove_empty_lines", "line1\n\n\n\nline2", {**BASE_OPTS_OFF, "remove_empty_lines": False},
       lambda r: r.count("\n") >= 3, "禁用：保留空行")

# 9. filter_watermark
verify("filter_watermark", "正文\nDRAFT\nDRAFT\nDRAFT\n其他", {**BASE_OPTS_OFF, "filter_watermark": True},
       lambda r: r.count("DRAFT") < 3, "启用：过滤水印重复行")
verify("filter_watermark", "正文\nDRAFT\nDRAFT\n其他", {**BASE_OPTS_OFF, "filter_watermark": True, "watermark_keywords": ["DRAFT"]},
       lambda r: "DRAFT" not in r, "启用+自定义关键词：过滤DRAFT")
verify("filter_watermark", "正文\nDRAFT\nDRAFT\n其他", {**BASE_OPTS_OFF, "filter_watermark": False},
       lambda r: "DRAFT" in r, "禁用：保留水印文本")

# 10. deduplicate_paragraphs
verify("deduplicate_paragraphs", "段落A\n\n段落A\n\n段落B", {**BASE_OPTS_OFF, "deduplicate_paragraphs": True},
       lambda r: r.count("段落A") == 1, "启用：精确去重")
verify("deduplicate_paragraphs", "段落A\n\n段落A\n\n段落B", {**BASE_OPTS_OFF, "deduplicate_paragraphs": True, "dedup_fuzzy": True},
       lambda r: "段落B" in r, "启用+模糊去重")
verify("deduplicate_paragraphs", "段落A\n\n段落A", {**BASE_OPTS_OFF, "deduplicate_paragraphs": False},
       lambda r: r.count("段落A") == 2, "禁用：保留重复段落")

# 11. clean_table
verify("clean_table", "| A | B |\n| --- | --- |\n|  |  |\n| 1 | 2 |", {**BASE_OPTS_OFF, "clean_table": True},
       lambda r: "|  |  |" not in r and "1" in r, "启用：移除表格空行")
verify("clean_table", "| A | B |\n| --- | --- |\n|  |  |\n| 1 | 2 |", {**BASE_OPTS_OFF, "clean_table": False},
       lambda r: "|  |  |" in r, "禁用：保留表格空行")

# 12. mask_sensitive
verify("mask_sensitive", "手机：13812345678", {**BASE_OPTS_OFF, "mask_sensitive": True},
       lambda r: "13812345678" not in r and "***" in r, "启用：脱敏手机号")
verify("mask_sensitive", "邮箱：test@example.com", {**BASE_OPTS_OFF, "mask_sensitive": True},
       lambda r: "test@example.com" not in r, "启用：脱敏邮箱")
verify("mask_sensitive", "手机：13812345678", {**BASE_OPTS_OFF, "mask_sensitive": False},
       lambda r: "13812345678" in r, "禁用：保留手机号")

# 13. filter_special_chars
verify("filter_special_chars", "hello★☆♦♣world", {**BASE_OPTS_OFF, "filter_special_chars": True},
       lambda r: "★" not in r, "启用：过滤特殊字符")
verify("filter_special_chars", "hello★world", {**BASE_OPTS_OFF, "filter_special_chars": False},
       lambda r: "★" in r, "禁用：保留特殊字符")

# 14. filter_toc
verify("filter_toc", "1.1 概述 ............ 1\n1.2 背景 ............ 5\n1.3 方法 ............ 10\n正文",
       {**BASE_OPTS_OFF, "filter_toc": True},
       lambda r: "1.1 概述" not in r or "............" not in r, "启用：过滤目录")
verify("filter_toc", "1.1 概述 ............ 1\n1.2 背景 ............ 5\n1.3 方法 ............ 10",
       {**BASE_OPTS_OFF, "filter_toc": False},
       lambda r: "1.1 概述" in r, "禁用：保留目录")

# 15. filter_page_numbers
verify("filter_page_numbers", "正文\n\n- 12 -\n\n更多", {**BASE_OPTS_OFF, "filter_page_numbers": True},
       lambda r: "- 12 -" not in r, "启用：移除页码")
verify("filter_page_numbers", "正文\n\n- 12 -\n\n更多", {**BASE_OPTS_OFF, "filter_page_numbers": False},
       lambda r: "- 12 -" in r, "禁用：保留页码")

# 16. process_footnotes
verify("process_footnotes", "正文[1]\n\n[1] 脚注内容", {**BASE_OPTS_OFF, "process_footnotes": True, "footnote_action": "remove"},
       lambda r: "脚注内容" not in r, "启用+remove：移除脚注")
verify("process_footnotes", "正文[1]\n\n[1] 脚注内容", {**BASE_OPTS_OFF, "process_footnotes": True, "footnote_action": "keep"},
       lambda r: "脚注内容" in r, "启用+keep：保留脚注")
verify("process_footnotes", "正文[1]\n\n[1] 脚注内容", {**BASE_OPTS_OFF, "process_footnotes": False},
       lambda r: "脚注内容" in r, "禁用：保留脚注")

# 17. remove_html_comments
verify("remove_html_comments", "正文<!-- 注释 -->内容", {**BASE_OPTS_OFF, "remove_html_comments": True},
       lambda r: "注释" not in r and "正文" in r, "启用：移除HTML注释")
verify("remove_html_comments", "正文<!-- 注释 -->内容", {**BASE_OPTS_OFF, "remove_html_comments": False},
       lambda r: "注释" in r, "禁用：保留HTML注释")

# 18. normalize_html_entities
verify("normalize_html_entities", "100&nbsp;元 &amp; 税费", {**BASE_OPTS_OFF, "normalize_html_entities": True},
       lambda r: "&nbsp;" not in r and "&amp;" not in r, "启用：转换HTML实体")
verify("normalize_html_entities", "100&nbsp;元", {**BASE_OPTS_OFF, "normalize_html_entities": False},
       lambda r: "&nbsp;" in r, "禁用：保留HTML实体")

# 19. filter_html_noise
verify("filter_html_noise", "正文\ncopyright © 2024 all rights reserved\n更多",
       {**BASE_OPTS_OFF, "filter_html_noise": True},
       lambda r: "copyright" not in r, "启用：过滤英文版权噪声")
verify("filter_html_noise", "正文\n版权所有 © 2024 保留所有权利\n更多",
       {**BASE_OPTS_OFF, "filter_html_noise": True},
       lambda r: "版权所有" not in r, "启用：过滤中文版权噪声")
verify("filter_html_noise", "正文\n限时秒杀限时秒杀限时秒杀限时秒杀\n其他",
       {**BASE_OPTS_OFF, "filter_html_noise": True, "html_ad_keywords": ["限时秒杀"]},
       lambda r: "限时秒杀" not in r, "启用+自定义广告关键词")
verify("filter_html_noise", "正文\n版权所有 © 2024\n更多",
       {**BASE_OPTS_OFF, "filter_html_noise": False},
       lambda r: "版权所有" in r, "禁用：保留噪声")

# 20. clean_markdown_links
verify("clean_markdown_links", "[link\ntext](url)", {**BASE_OPTS_OFF, "clean_markdown_links": True},
       lambda r: "linktext" in r and "\n" not in r.split("](url)")[0], "启用：移除链接换行")
verify("clean_markdown_links", "[link\ntext](url)", {**BASE_OPTS_OFF, "clean_markdown_links": False},
       lambda r: "link\ntext" in r, "禁用：保留链接换行")

# 21. remove_md_escapes
verify("remove_md_escapes", "hello\\*world", {**BASE_OPTS_OFF, "remove_md_escapes": True},
       lambda r: "\\*" not in r and "hello*world" in r, "启用：移除MD转义")
verify("remove_md_escapes", "hello\\*world", {**BASE_OPTS_OFF, "remove_md_escapes": False},
       lambda r: "\\*" in r, "禁用：保留MD转义")

# 22. clean_md_structure
verify("clean_md_structure", "  # 标题", {**BASE_OPTS_OFF, "clean_md_structure": True},
       lambda r: "# 标题" in r, "启用：移除标题前空格")
verify("clean_md_structure", "  # 标题", {**BASE_OPTS_OFF, "clean_md_structure": False},
       lambda r: "  # 标题" in r, "禁用：保留标题前空格")

# 前端参数映射验证
verify("前端参数映射", "正文\nDRAFT\nDRAFT\n其他",
       {**BASE_OPTS_OFF, "filter_watermark": True, "watermark_keywords": ["DRAFT"]},
       lambda r: "DRAFT" not in r, "watermark_keywords 数组传递")

verify("前端参数映射", "正文\n广告位招商\n其他",
       {**BASE_OPTS_OFF, "filter_html_noise": True, "html_noise_patterns": ["广告位.*"]},
       lambda r: "广告位招商" not in r, "html_noise_patterns 数组传递")

verify("前端参数映射", "正文\n限时秒杀限时秒杀限时秒杀限时秒杀\n其他",
       {**BASE_OPTS_OFF, "filter_html_noise": True, "html_ad_keywords": ["限时秒杀"]},
       lambda r: "限时秒杀" not in r, "html_ad_keywords 数组传递")

# Profile 预设验证
verify_profile("Profile:default", "正文<!-- 注释 -->内容", "default",
       lambda r: "注释" in r, "default 预设：HTML注释保留")
verify_profile("Profile:web_content", "正文<!-- 注释 -->内容", "web_content",
       lambda r: "注释" not in r, "web_content 预设：HTML注释移除")
verify_profile("Profile:pdf_academic", "1.1 概述 ............ 1\n1.2 背景 ............ 5\n1.3 方法 ............ 10\n正文",
       "pdf_academic",
       lambda r: "1.1 概述" not in r or "............" not in r, "pdf_academic 预设：目录过滤")
verify_profile("Profile:pdf_business", "正文\nDRAFT\nDRAFT\nDRAFT\n更多",
       "pdf_business",
       lambda r: r.count("DRAFT") < 3, "pdf_business 预设：水印过滤")
verify_profile("Profile:docx_report", "1.1 概述 ............ 1\n1.2 背景 ............ 5\n1.3 方法 ............ 10\n正文",
       "docx_report",
       lambda r: "1.1 概述" not in r or "............" not in r, "docx_report 预设：目录过滤")
verify_profile("Profile:table_data", "| A | B |\n| --- | --- |\n|  |  |\n| 1 | 2 |",
       "table_data",
       lambda r: "|  |  |" not in r, "table_data 预设：表格清洗")
verify_profile("Profile:legal", "1.1 概述 ............ 1\n1.2 背景 ............ 5\n1.3 方法 ............ 10\n正文",
       "legal",
       lambda r: "1.1 概述" not in r or "............" not in r, "legal 预设：目录过滤")

# 输出报告
print("=" * 80)
print("数据清洗规则验证报告：前端选型 → 后端 /api/clean 端点")
print("=" * 80)
print()
for i, r in enumerate(results, 1):
    status = "✅" if r["result"] == "PASS" else "❌"
    print(f"{status} [{i:02d}] {r['rule']}: {r['desc']}")
    if r["result"] != "PASS":
        print(f"       输入: {r['input']}")
        print(f"       实际: {r['actual']}")

print()
print("-" * 80)
print(f"总计: {total} | 通过: {passed} | 失败: {failed}")
print("-" * 80)

if failed > 0:
    print("\n❌ 存在失败项，请检查上方详情")
    sys.exit(1)
else:
    print("\n✅ 全部规则验证通过，前端清洗选型 → 后端功能完全一致")
    sys.exit(0)
