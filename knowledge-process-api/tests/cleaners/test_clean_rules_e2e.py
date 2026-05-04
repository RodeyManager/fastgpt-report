"""
端到端验证：前端清洗选型 → 后端 /api/clean 是否生效
逐条启用每条规则，验证后端清洗结果是否符合预期。
"""

import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _ensure_profiles():
    from fastgpt_demo.cleaners.profiles import _load_builtins, _reset_loaded
    from fastgpt_demo.cleaners.profiles.registry import clear_profiles
    clear_profiles()
    _reset_loaded()
    _load_builtins()
    yield
    clear_profiles()
    _reset_loaded()
    _load_builtins()

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


def _clean(text: str, opts: dict) -> str:
    resp = client.post("/api/clean", json={"text": text, "options": opts})
    assert resp.status_code == 200, f"API 返回错误: {resp.text}"
    return resp.json()["cleaned"]


class TestTrimRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "trim": True}
        result = _clean("  hello world  ", opts)
        assert result == "hello world"

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "trim": False}
        result = _clean("  hello world  ", opts)
        assert result == "  hello world  "


class TestNormalizeUnicodeRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "normalize_unicode": True}
        result = _clean("Ｈｅｌｌｏ", opts)
        assert "Hello" in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "normalize_unicode": False}
        result = _clean("Ｈｅｌｌｏ", opts)
        assert "Ｈｅｌｌｏ" in result


class TestRemoveInvisibleCharsRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "remove_invisible_chars": True}
        result = _clean("hello\u200bworld", opts)
        assert "\u200b" not in result
        assert "helloworld" in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "remove_invisible_chars": False}
        result = _clean("hello\u200bworld", opts)
        assert "\u200b" in result


class TestRemoveChineseSpaceRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "remove_chinese_space": True}
        result = _clean("你好 世界", opts)
        assert "你好世界" in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "remove_chinese_space": False}
        result = _clean("你好 世界", opts)
        assert "你好 世界" in result


class TestNormalizeNewlineRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "normalize_newline": True}
        result = _clean("line1\r\nline2\rline3", opts)
        assert "\r" not in result
        assert "\r\n" not in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "normalize_newline": False}
        result = _clean("line1\r\nline2", opts)
        assert "\r" in result


class TestFixHyphenationRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "fix_hyphenation": True}
        result = _clean("knowl-\nedge", opts)
        assert "knowledge" in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "fix_hyphenation": False}
        result = _clean("knowl-\nedge", opts)
        assert "knowl-\nedge" in result


class TestCollapseWhitespaceRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "collapse_whitespace": True}
        result = _clean("hello    world", opts)
        assert "hello world" in result
        assert "    " not in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "collapse_whitespace": False}
        result = _clean("hello    world", opts)
        assert "    " in result


class TestRemoveEmptyLinesRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "remove_empty_lines": True}
        result = _clean("line1\n\n\n\nline2", opts)
        assert result.count("\n") <= 2

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "remove_empty_lines": False}
        result = _clean("line1\n\n\n\nline2", opts)
        assert result.count("\n") >= 3


class TestFilterWatermarkRule:
    def test_enabled_repeat_lines(self):
        opts = {**BASE_OPTS_OFF, "filter_watermark": True}
        text = "正文内容\n机密文件\n机密文件\n机密文件\n其他内容"
        result = _clean(text, opts)
        assert result.count("机密文件") < 3

    def test_enabled_custom_keywords(self):
        opts = {**BASE_OPTS_OFF, "filter_watermark": True, "watermark_keywords": ["DRAFT"]}
        text = "正文内容\nDRAFT\nDRAFT\n其他内容"
        result = _clean(text, opts)
        assert "DRAFT" not in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "filter_watermark": False}
        text = "正文内容\nDRAFT\nDRAFT\n其他内容"
        result = _clean(text, opts)
        assert "DRAFT" in result


class TestDeduplicateParagraphsRule:
    def test_enabled_exact(self):
        opts = {**BASE_OPTS_OFF, "deduplicate_paragraphs": True}
        text = "第一段内容\n\n第一段内容\n\n第二段内容"
        result = _clean(text, opts)
        assert result.count("第一段内容") == 1

    def test_enabled_fuzzy(self):
        opts = {**BASE_OPTS_OFF, "deduplicate_paragraphs": True, "dedup_fuzzy": True}
        text = "这是一段很长的文本内容描述\n\n这是一段很长的文本内容描述，略有不同\n\n其他内容"
        result = _clean(text, opts)
        assert "其他内容" in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "deduplicate_paragraphs": False}
        text = "第一段内容\n\n第一段内容"
        result = _clean(text, opts)
        assert result.count("第一段内容") == 2


class TestCleanTableRule:
    def test_enabled_removes_empty_rows(self):
        opts = {**BASE_OPTS_OFF, "clean_table": True}
        text = "| 姓名 | 年龄 |\n| --- | --- |\n|  |  |\n| 张三 | 25 |"
        result = _clean(text, opts)
        assert "|  |  |" not in result
        assert "张三" in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "clean_table": False}
        text = "| 姓名 | 年龄 |\n| --- | --- |\n|  |  |\n| 张三 | 25 |"
        result = _clean(text, opts)
        assert "|  |  |" in result


class TestMaskSensitiveRule:
    def test_enabled_phone(self):
        opts = {**BASE_OPTS_OFF, "mask_sensitive": True}
        result = _clean("联系电话：13812345678", opts)
        assert "13812345678" not in result
        assert "***" in result

    def test_enabled_email(self):
        opts = {**BASE_OPTS_OFF, "mask_sensitive": True}
        result = _clean("邮箱：test@example.com", opts)
        assert "test@example.com" not in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "mask_sensitive": False}
        result = _clean("联系电话：13812345678", opts)
        assert "13812345678" in result


class TestFilterSpecialCharsRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "filter_special_chars": True}
        result = _clean("hello★☆♦♣world", opts)
        assert "★" not in result
        assert "☆" not in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "filter_special_chars": False}
        result = _clean("hello★world", opts)
        assert "★" in result


class TestFilterTocRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "filter_toc": True}
        text = "1.1 概述 ............ 1\n1.2 背景 ............ 5\n1.3 方法 ............ 10\n正文内容开始"
        result = _clean(text, opts)
        assert "............" not in result or "1.1 概述" not in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "filter_toc": False}
        text = "1.1 概述 ............ 1\n1.2 背景 ............ 5\n1.3 方法 ............ 10"
        result = _clean(text, opts)
        assert "1.1 概述" in result


class TestFilterPageNumbersRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "filter_page_numbers": True}
        text = "正文内容\n\n- 12 -\n\n更多内容"
        result = _clean(text, opts)
        assert "- 12 -" not in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "filter_page_numbers": False}
        text = "正文内容\n\n- 12 -\n\n更多内容"
        result = _clean(text, opts)
        assert "- 12 -" in result


class TestProcessFootnotesRule:
    def test_enabled_remove(self):
        opts = {**BASE_OPTS_OFF, "process_footnotes": True, "footnote_action": "remove"}
        text = "正文内容[1]\n\n[1] 这是脚注内容"
        result = _clean(text, opts)
        assert "脚注内容" not in result

    def test_enabled_keep(self):
        opts = {**BASE_OPTS_OFF, "process_footnotes": True, "footnote_action": "keep"}
        text = "正文内容[1]\n\n[1] 这是脚注内容"
        result = _clean(text, opts)
        assert "脚注内容" in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "process_footnotes": False}
        text = "正文内容[1]\n\n[1] 这是脚注内容"
        result = _clean(text, opts)
        assert "脚注内容" in result


class TestRemoveHtmlCommentsRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "remove_html_comments": True}
        result = _clean("正文<!-- 这是注释 -->更多内容", opts)
        assert "注释" not in result
        assert "正文" in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "remove_html_comments": False}
        result = _clean("正文<!-- 这是注释 -->更多内容", opts)
        assert "注释" in result


class TestNormalizeHtmlEntitiesRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "normalize_html_entities": True}
        result = _clean("价格：100&nbsp;元 &amp; 税费", opts)
        assert "\u00a0" not in result or " " in result
        assert "&" in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "normalize_html_entities": False}
        result = _clean("100&nbsp;元", opts)
        assert "&nbsp;" in result


class TestFilterHtmlNoiseRule:
    def test_enabled_builtin(self):
        opts = {**BASE_OPTS_OFF, "filter_html_noise": True}
        text = "正文内容\ncopyright © 2024 all rights reserved\n更多内容"
        result = _clean(text, opts)
        assert "copyright" not in result

    def test_enabled_chinese_copyright(self):
        opts = {**BASE_OPTS_OFF, "filter_html_noise": True}
        text = "正文内容\n版权所有 © 2024 保留所有权利\n更多内容"
        result = _clean(text, opts)
        assert "版权所有" not in result

    def test_enabled_custom_keywords(self):
        opts = {**BASE_OPTS_OFF, "filter_html_noise": True, "html_ad_keywords": ["限时优惠"]}
        text = "正文内容\n限时优惠，点击购买\n更多内容"
        result = _clean(text, opts)
        assert "限时优惠" not in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "filter_html_noise": False}
        text = "正文内容\n版权所有 © 2024\n更多内容"
        result = _clean(text, opts)
        assert "版权所有" in result


class TestCleanMarkdownLinksRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "clean_markdown_links": True}
        result = _clean("[link\ntext](url)", opts)
        assert "linktext" in result
        assert "\n" not in result.split("](url)")[0]

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "clean_markdown_links": False}
        result = _clean("[link\ntext](url)", opts)
        assert "link\ntext" in result


class TestRemoveMdEscapesRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "remove_md_escapes": True}
        result = _clean("hello\\*world", opts)
        assert "\\*" not in result
        assert "hello*world" in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "remove_md_escapes": False}
        result = _clean("hello\\*world", opts)
        assert "\\*" in result


class TestCleanMdStructureRule:
    def test_enabled(self):
        opts = {**BASE_OPTS_OFF, "clean_md_structure": True}
        result = _clean("  # 标题", opts)
        assert "# 标题" in result

    def test_disabled(self):
        opts = {**BASE_OPTS_OFF, "clean_md_structure": False}
        result = _clean("  # 标题", opts)
        assert "  # 标题" in result


class TestFrontendParamMapping:
    """验证前端参数名与后端 CleanOptions 字段完全匹配。"""

    def test_all_frontend_keys_exist_in_backend(self):
        from app import CleanOptions
        import json

        frontend_opts = {
            "trim": True, "normalize_unicode": True, "remove_invisible_chars": True,
            "remove_chinese_space": True, "normalize_newline": True, "fix_hyphenation": True,
            "collapse_whitespace": True, "remove_empty_lines": True,
            "remove_html_comments": False, "normalize_html_entities": False,
            "filter_html_noise": False, "html_noise_patterns": [], "html_ad_keywords": [],
            "filter_watermark": False, "watermark_keywords": "",
            "filter_toc": False, "filter_page_numbers": False,
            "process_footnotes": False, "footnote_action": "remove",
            "deduplicate_paragraphs": False, "dedup_fuzzy": False,
            "clean_table": False, "clean_markdown_links": True,
            "remove_md_escapes": True, "clean_md_structure": True,
            "mask_sensitive": False, "filter_special_chars": False,
        }

        backend_fields = set(CleanOptions.model_fields.keys())
        for key in frontend_opts:
            assert key in backend_fields, f"前端字段 '{key}' 在后端 CleanOptions 中不存在"

    def test_watermark_keywords_string_to_array(self):
        """前端 watermark_keywords 为字符串，API 调用前会转为数组。"""
        opts = {**BASE_OPTS_OFF, "filter_watermark": True, "watermark_keywords": ["DRAFT", "机密"]}
        text = "正文\nDRAFT\nDRAFT\n其他"
        result = _clean(text, opts)
        assert "DRAFT" not in result

    def test_html_noise_patterns_array(self):
        """前端 html_noise_patterns 字符串转数组后传递。"""
        opts = {**BASE_OPTS_OFF, "filter_html_noise": True, "html_noise_patterns": ["广告位.*"]}
        text = "正文\n广告位招商\n其他"
        result = _clean(text, opts)
        assert "广告位招商" not in result

    def test_html_ad_keywords_array(self):
        opts = {**BASE_OPTS_OFF, "filter_html_noise": True, "html_ad_keywords": ["限时秒杀"]}
        text = "正文\n限时秒杀限时秒杀限时秒杀限时秒杀\n其他"
        result = _clean(text, opts)
        assert "限时秒杀" not in result


class TestProfileEffect:
    """验证 Profile 预设切换后规则是否正确生效。"""

    def test_default_profile_no_html_cleaning(self):
        resp = client.post("/api/clean", json={
            "text": "正文<!-- 注释 -->内容",
            "profile": "default"
        })
        assert resp.status_code == 200
        result = resp.json()["cleaned"]
        assert "注释" in result

    def test_web_content_profile_enables_html_cleaning(self):
        resp = client.post("/api/clean", json={
            "text": "正文<!-- 注释 -->内容",
            "profile": "web_content"
        })
        assert resp.status_code == 200
        result = resp.json()["cleaned"]
        assert "注释" not in result

    def test_pdf_academic_profile_enables_toc_filter(self):
        resp = client.post("/api/clean", json={
            "text": "1.1 概述 ............ 1\n1.2 背景 ............ 5\n1.3 方法 ............ 10\n正文",
            "profile": "pdf_academic"
        })
        assert resp.status_code == 200
        result = resp.json()["cleaned"]
        assert "............" not in result or "1.1 概述" not in result

    def test_table_data_profile_enables_table_clean(self):
        resp = client.post("/api/clean", json={
            "text": "| A | B |\n| --- | --- |\n|  |  |\n| 1 | 2 |",
            "profile": "table_data"
        })
        assert resp.status_code == 200
        result = resp.json()["cleaned"]
        assert "|  |  |" not in result
