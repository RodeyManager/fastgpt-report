# P2 数据清洗规则实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 P0/P1 基础上，补齐结构级清洗规则、HTML 内容过滤能力、CleanProfile 预设机制，并完成清洗与转换的解耦。

**Architecture:** 基于 CleanRule 基类 + 注册表 + 管道的现有架构，新增 9 条清洗规则（Markdown 后处理 3 条、结构级 3 条、HTML 清洗 3 条），新增 CleanProfile 预设机制（7 个预设），修改 HTML 解析器增加干扰标签移除和内容区域识别，解耦 markdown_converter 与 cleaners 的逻辑重复。

**Tech Stack:** Python 3.12+ / FastAPI / Pydantic / BeautifulSoup4 / Vue 3

**Spec:** [2026-05-01-data-cleaning-implementation-plan.md](file:///d:/service/py-project/rag-project/fastgpt-report/docs/superpowers/specs/2026-05-01-data-cleaning-implementation-plan.md)

---

## File Structure

| 文件 | 职责 | 变更类型 |
|------|------|---------|
| `cleaners/rules/markdown_post.py` | Markdown 后处理规则（3 个 Rule） | 新增 |
| `cleaners/rules/toc_filter.py` | 目录区域过滤规则 | 新增 |
| `cleaners/rules/page_number.py` | 页码过滤规则 | 新增 |
| `cleaners/rules/footnote.py` | 脚注/尾注处理规则 | 新增 |
| `cleaners/rules/html_clean.py` | HTML 清洗规则（3 个 Rule） | 新增 |
| `cleaners/rules/__init__.py` | 注册所有新规则 | 修改 |
| `cleaners/profiles/__init__.py` | Profile 模块导出 | 新增 |
| `cleaners/profiles/base.py` | CleanProfile 基类 | 新增 |
| `cleaners/profiles/registry.py` | Profile 注册表 | 新增 |
| `cleaners/profiles/default.py` | 默认配置 | 新增 |
| `cleaners/profiles/pdf_academic.py` | 学术 PDF 配置 | 新增 |
| `cleaners/profiles/pdf_business.py` | 商务 PDF 配置 | 新增 |
| `cleaners/profiles/docx_report.py` | DOCX 报告配置 | 新增 |
| `cleaners/profiles/table_data.py` | 表格数据配置 | 新增 |
| `cleaners/profiles/legal.py` | 法律文书配置 | 新增 |
| `cleaners/profiles/web_content.py` | 网页内容配置 | 新增 |
| `cleaners/text_cleaner.py` | 支持 Profile | 修改 |
| `cleaners/__init__.py` | 更新导出 | 修改 |
| `parsers/html_parser.py` | 干扰标签移除 + 内容区域识别 | 修改 |
| `parsers/__init__.py` | 传递 remove_html_noise 参数 | 修改 |
| `converters/markdown_converter.py` | simple_text() 委托 cleaners | 修改 |
| `app.py` | CleanOptions 新增 P2 字段 + profile + remove_html_noise | 修改 |
| `KnowledgeProcessDemo.vue` | 预设选择器 + P2 规则控件 + HTML 选项 | 修改 |

---

### Task 1: Markdown 后处理规则化

**Files:**
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/rules/markdown_post.py`
- Modify: `knowledge-process-api/src/fastgpt_demo/cleaners/rules/__init__.py`
- Modify: `knowledge-process-api/app.py`
- Test: `knowledge-process-api/tests/test_markdown_post_rule.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_markdown_post_rule.py
import pytest
from fastgpt_demo.cleaners.base import CleanRule
from fastgpt_demo.cleaners.registry import get, get_all_rules, clear
from fastgpt_demo.cleaners.pipeline import CleanPipeline
from fastgpt_demo.cleaners import rules as _rules  # noqa: F401


@pytest.fixture(autouse=True)
def _clean_registry():
    clear()
    from fastgpt_demo.cleaners.rules import whitespace, unicode, chinese_text
    from fastgpt_demo.cleaners.rules import hyphenation, sensitive, special_chars
    from fastgpt_demo.cleaners.rules import watermark, deduplication, table_clean
    from fastgpt_demo.cleaners.rules import markdown_post
    yield
    clear()


class TestCleanMarkdownLinksRule:
    def test_removes_newlines_in_link_text(self):
        rule = get("clean_markdown_links")
        text = "[hello\nworld](http://example.com)"
        result = rule.apply(text)
        assert result == "[helloworld](http://example.com)"

    def test_preserves_link_without_newlines(self):
        rule = get("clean_markdown_links")
        text = "[hello](http://example.com)"
        result = rule.apply(text)
        assert result == "[hello](http://example.com)"

    def test_preserves_plain_text(self):
        rule = get("clean_markdown_links")
        text = "普通文本没有链接"
        result = rule.apply(text)
        assert result == "普通文本没有链接"


class TestRemoveMdEscapesRule:
    def test_removes_backslash_escapes(self):
        rule = get("remove_md_escapes")
        text = r"hello \*world\* and \#heading"
        result = rule.apply(text)
        assert result == "hello *world* and #heading"

    def test_preserves_normal_text(self):
        rule = get("remove_md_escapes")
        text = "hello world"
        result = rule.apply(text)
        assert result == "hello world"


class TestCleanMdStructureRule:
    def test_removes_leading_spaces_before_heading(self):
        rule = get("clean_md_structure")
        text = "text\n  ## heading"
        result = rule.apply(text)
        assert result == "text\n## heading"

    def test_removes_leading_spaces_before_code_block(self):
        rule = get("clean_md_structure")
        text = "text\n  ```python"
        result = rule.apply(text)
        assert result == "text\n```python"

    def test_preserves_heading_without_spaces(self):
        rule = get("clean_md_structure")
        text = "text\n## heading"
        result = rule.apply(text)
        assert result == "text\n## heading"


class TestMarkdownPostInPipeline:
    def test_pipeline_applies_markdown_post_rules(self):
        pipeline = CleanPipeline()
        text = "[hello\nworld](url)  \\*bold\\*  \n  ## heading"
        result = pipeline.execute(text, {
            "clean_markdown_links": True,
            "remove_md_escapes": True,
            "clean_md_structure": True,
        })
        assert "[hello" not in result or "world](url)" not in result
        assert "\\*" not in result
        assert "## heading" in result
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd knowledge-process-api && python -m pytest tests/test_markdown_post_rule.py -v`
Expected: FAIL — `markdown_post` 模块不存在

- [ ] **Step 3: 实现 Markdown 后处理规则**

```python
# src/fastgpt_demo/cleaners/rules/markdown_post.py
from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class CleanMarkdownLinksRule(CleanRule):
    name = "clean_markdown_links"
    description = "移除 Markdown 链接文本中的换行"
    default_enabled = True

    _LINK_RE = re.compile(r"\[([^\]]+)\]\((.+?)\)")

    def apply(self, text: str, **kwargs) -> str:
        def _clean_link(m: re.Match) -> str:
            link_text = m.group(1).replace("\n", "")
            url = m.group(2)
            if not url:
                return link_text
            return f"[{link_text}]({url})"
        return self._LINK_RE.sub(_clean_link, text)


class RemoveMdEscapesRule(CleanRule):
    name = "remove_md_escapes"
    description = "移除不必要的 Markdown 反斜杠转义"
    default_enabled = True

    _UNESCAPE_RE = re.compile(r"\\([#`!*+\-\_[\]{}\\.()])")

    def apply(self, text: str, **kwargs) -> str:
        if not self._UNESCAPE_RE.search(text):
            return text
        return self._UNESCAPE_RE.sub(r"\1", text)


class CleanMdStructureRule(CleanRule):
    name = "clean_md_structure"
    description = "移除 Markdown 结构元素前的多余空格"
    default_enabled = True

    _STRUCTURE_PATTERNS = ["####", "###", "##", "#", "```", "~~~"]

    def apply(self, text: str, **kwargs) -> str:
        for pattern in self._STRUCTURE_PATTERNS:
            if re.search(r"\n\s*" + re.escape(pattern), text):
                text = re.sub(
                    r"\n( *)(" + re.escape(pattern) + r")",
                    r"\n\2",
                    text,
                )
        return text


register(CleanMarkdownLinksRule())
register(RemoveMdEscapesRule())
register(CleanMdStructureRule())
```

- [ ] **Step 4: 注册新规则到 `__init__.py`**

在 `cleaners/rules/__init__.py` 末尾添加：

```python
from . import markdown_post
```

- [ ] **Step 5: 运行测试确认通过**

Run: `cd knowledge-process-api && python -m pytest tests/test_markdown_post_rule.py -v`
Expected: PASS

- [ ] **Step 6: 更新 `app.py` CleanOptions**

在 `CleanOptions` 类中添加三个新字段（在 `filter_special_chars` 之后）：

```python
    clean_markdown_links: bool = True
    remove_md_escapes: bool = True
    clean_md_structure: bool = True
```

- [ ] **Step 7: 运行全量测试确认无回归**

Run: `cd knowledge-process-api && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 8: 提交**

```bash
git add knowledge-process-api/src/fastgpt_demo/cleaners/rules/markdown_post.py
git add knowledge-process-api/src/fastgpt_demo/cleaners/rules/__init__.py
git add knowledge-process-api/app.py
git add knowledge-process-api/tests/test_markdown_post_rule.py
git commit -m "feat: add markdown post-processing rules (clean_markdown_links, remove_md_escapes, clean_md_structure)"
```

---

### Task 2: 目录区域过滤规则

**Files:**
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/rules/toc_filter.py`
- Modify: `knowledge-process-api/src/fastgpt_demo/cleaners/rules/__init__.py`
- Modify: `knowledge-process-api/app.py`
- Test: `knowledge-process-api/tests/test_toc_filter_rule.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_toc_filter_rule.py
import pytest
from fastgpt_demo.cleaners.registry import get, clear
from fastgpt_demo.cleaners import rules as _rules  # noqa: F401


@pytest.fixture(autouse=True)
def _setup():
    clear()
    from fastgpt_demo.cleaners.rules import toc_filter
    yield
    clear()


class TestFilterTocRule:
    def test_removes_numeric_toc(self):
        rule = get("filter_toc")
        text = "1.1 概述 .... 12\n1.2 背景 .... 15\n1.3 方法 .... 20\n正文内容"
        result = rule.apply(text)
        assert "1.1 概述" not in result
        assert "正文内容" in result

    def test_removes_chinese_chapter_toc(self):
        rule = get("filter_toc")
        text = "第一章 引言\n第二章 方法\n第三章 结果\n正文内容"
        result = rule.apply(text)
        assert "第一章" not in result
        assert "正文内容" in result

    def test_preserves_short_numbered_list(self):
        rule = get("filter_toc")
        text = "1. 第一点\n2. 第二点\n正文内容"
        result = rule.apply(text)
        assert "1. 第一点" in result

    def test_preserves_normal_text(self):
        rule = get("filter_toc")
        text = "这是一段普通文本\n没有目录格式"
        result = rule.apply(text)
        assert result == text

    def test_toc_needs_three_consecutive_lines(self):
        rule = get("filter_toc")
        text = "1.1 概述 .... 12\n1.2 背景 .... 15\n正文内容"
        result = rule.apply(text)
        assert "1.1 概述" in result
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd knowledge-process-api && python -m pytest tests/test_toc_filter_rule.py -v`
Expected: FAIL — `toc_filter` 模块不存在

- [ ] **Step 3: 实现目录过滤规则**

```python
# src/fastgpt_demo/cleaners/rules/toc_filter.py
from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class FilterTocRule(CleanRule):
    name = "filter_toc"
    description = "检测并移除自动生成的目录区域（需 ≥3 行连续目录条目）"
    default_enabled = False

    _TOC_PATTERNS = [
        re.compile(r"^\d+(\.\d+)*\s+.+\s*\.{2,}\s*\d+\s*$"),
        re.compile(r"^第[一二三四五六七八九十\d]+[章节篇]\s+.+$"),
        re.compile(r"^[附录附件]\s*[A-Z\d]*\s+.+$"),
    ]

    _MIN_CONSECUTIVE = 3

    def apply(self, text: str, **kwargs) -> str:
        lines = text.split("\n")
        is_toc_line = [self._match_toc(line) for line in lines]

        result_lines = []
        i = 0
        while i < len(lines):
            if is_toc_line[i]:
                run_start = i
                while i < len(lines) and is_toc_line[i]:
                    i += 1
                run_len = i - run_start
                if run_len < self._MIN_CONSECUTIVE:
                    for j in range(run_start, i):
                        result_lines.append(lines[j])
            else:
                result_lines.append(lines[i])
                i += 1

        return "\n".join(result_lines)

    def _match_toc(self, line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False
        for pattern in self._TOC_PATTERNS:
            if pattern.match(stripped):
                return True
        return False


register(FilterTocRule())
```

- [ ] **Step 4: 注册新规则**

在 `cleaners/rules/__init__.py` 末尾添加：

```python
from . import toc_filter
```

- [ ] **Step 5: 更新 `app.py` CleanOptions**

在 `clean_md_structure` 之后添加：

```python
    filter_toc: bool = False
```

- [ ] **Step 6: 运行测试确认通过**

Run: `cd knowledge-process-api && python -m pytest tests/test_toc_filter_rule.py -v`
Expected: PASS

- [ ] **Step 7: 运行全量测试**

Run: `cd knowledge-process-api && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 8: 提交**

```bash
git add knowledge-process-api/src/fastgpt_demo/cleaners/rules/toc_filter.py
git add knowledge-process-api/src/fastgpt_demo/cleaners/rules/__init__.py
git add knowledge-process-api/app.py
git add knowledge-process-api/tests/test_toc_filter_rule.py
git commit -m "feat: add TOC area filter rule (filter_toc)"
```

---

### Task 3: 页码过滤规则

**Files:**
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/rules/page_number.py`
- Modify: `knowledge-process-api/src/fastgpt_demo/cleaners/rules/__init__.py`
- Modify: `knowledge-process-api/app.py`
- Test: `knowledge-process-api/tests/test_page_number_rule.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_page_number_rule.py
import pytest
from fastgpt_demo.cleaners.registry import get, clear
from fastgpt_demo.cleaners import rules as _rules  # noqa: F401


@pytest.fixture(autouse=True)
def _setup():
    clear()
    from fastgpt_demo.cleaners.rules import page_number
    yield
    clear()


class TestFilterPageNumbersRule:
    def test_removes_bare_number(self):
        rule = get("filter_page_numbers")
        text = "正文内容\n12\n更多正文"
        result = rule.apply(text)
        assert "正文内容" in result
        assert "更多正文" in result
        assert "\n12\n" not in result

    def test_removes_dashed_page_number(self):
        rule = get("filter_page_numbers")
        text = "正文\n- 5 -\n更多正文"
        result = rule.apply(text)
        assert "- 5 -" not in result

    def test_removes_chinese_page_number(self):
        rule = get("filter_page_numbers")
        text = "正文\n第 12 页\n更多正文"
        result = rule.apply(text)
        assert "第 12 页" not in result

    def test_removes_english_page_number(self):
        rule = get("filter_page_numbers")
        text = "正文\nPage 42\n更多正文"
        result = rule.apply(text)
        assert "Page 42" not in result

    def test_preserves_number_in_text(self):
        rule = get("filter_page_numbers")
        text = "共有 12 个项目"
        result = rule.apply(text)
        assert "共有 12 个项目" in result

    def test_preserves_number_with_other_content(self):
        rule = get("filter_page_numbers")
        text = "12 个苹果"
        result = rule.apply(text)
        assert "12 个苹果" in result
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd knowledge-process-api && python -m pytest tests/test_page_number_rule.py -v`
Expected: FAIL

- [ ] **Step 3: 实现页码过滤规则**

```python
# src/fastgpt_demo/cleaners/rules/page_number.py
from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class FilterPageNumbersRule(CleanRule):
    name = "filter_page_numbers"
    description = "移除独立成行的页码文本"
    default_enabled = False

    _PAGE_PATTERNS = [
        re.compile(r"^\s*\d{1,4}\s*$"),
        re.compile(r"^\s*[-—–]\s*\d{1,4}\s*[-—–]\s*$"),
        re.compile(r"^\s*第\s*\d{1,4}\s*页\s*$"),
        re.compile(r"^\s*[Pp]age\s+\d{1,4}\s*$"),
    ]

    def apply(self, text: str, **kwargs) -> str:
        lines = text.split("\n")
        result_lines = [line for line in lines if not self._is_page_number(line)]
        return "\n".join(result_lines)

    def _is_page_number(self, line: str) -> bool:
        if not line.strip():
            return False
        return any(p.match(line) for p in self._PAGE_PATTERNS)


register(FilterPageNumbersRule())
```

- [ ] **Step 4: 注册新规则**

在 `cleaners/rules/__init__.py` 末尾添加：

```python
from . import page_number
```

- [ ] **Step 5: 更新 `app.py` CleanOptions**

在 `filter_toc` 之后添加：

```python
    filter_page_numbers: bool = False
```

- [ ] **Step 6: 运行测试确认通过**

Run: `cd knowledge-process-api && python -m pytest tests/test_page_number_rule.py -v`
Expected: PASS

- [ ] **Step 7: 运行全量测试**

Run: `cd knowledge-process-api && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 8: 提交**

```bash
git add knowledge-process-api/src/fastgpt_demo/cleaners/rules/page_number.py
git add knowledge-process-api/src/fastgpt_demo/cleaners/rules/__init__.py
git add knowledge-process-api/app.py
git add knowledge-process-api/tests/test_page_number_rule.py
git commit -m "feat: add page number filter rule (filter_page_numbers)"
```

---

### Task 4: 脚注/尾注处理规则

**Files:**
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/rules/footnote.py`
- Modify: `knowledge-process-api/src/fastgpt_demo/cleaners/rules/__init__.py`
- Modify: `knowledge-process-api/app.py`
- Test: `knowledge-process-api/tests/test_footnote_rule.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_footnote_rule.py
import pytest
from fastgpt_demo.cleaners.registry import get, clear
from fastgpt_demo.cleaners import rules as _rules  # noqa: F401


@pytest.fixture(autouse=True)
def _setup():
    clear()
    from fastgpt_demo.cleaners.rules import footnote
    yield
    clear()


class TestProcessFootnotesRule:
    def test_removes_footnotes_by_default(self):
        rule = get("process_footnotes")
        text = "正文内容[1]\n1 脚注内容说明\n更多正文"
        result = rule.apply(text, footnote_action="remove")
        assert "1 脚注内容说明" not in result
        assert "正文内容" in result

    def test_keeps_footnotes_when_action_keep(self):
        rule = get("process_footnotes")
        text = "正文内容[1]\n1 脚注内容说明\n更多正文"
        result = rule.apply(text, footnote_action="keep")
        assert "1 脚注内容说明" in result

    def test_removes_circled_number_footnotes(self):
        rule = get("process_footnotes")
        text = "正文①内容\n①脚注说明\n更多正文"
        result = rule.apply(text, footnote_action="remove")
        assert "①脚注说明" not in result

    def test_preserves_normal_numbered_list(self):
        rule = get("process_footnotes")
        text = "1. 第一点内容\n2. 第二点内容\n正文"
        result = rule.apply(text, footnote_action="remove")
        assert "1. 第一点内容" in result

    def test_normal_text_unchanged(self):
        rule = get("process_footnotes")
        text = "普通文本没有脚注"
        result = rule.apply(text, footnote_action="remove")
        assert result == "普通文本没有脚注"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd knowledge-process-api && python -m pytest tests/test_footnote_rule.py -v`
Expected: FAIL

- [ ] **Step 3: 实现脚注处理规则**

```python
# src/fastgpt_demo/cleaners/rules/footnote.py
from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class ProcessFootnotesRule(CleanRule):
    name = "process_footnotes"
    description = "识别脚注/尾注，可选保留或移除"
    default_enabled = False

    _FOOTNOTE_MARKER_RE = re.compile(r"\[\d+\]|\^\d+|[①②③④⑤⑥⑦⑧⑨⑩]")
    _FOOTNOTE_LINE_RE = re.compile(r"^(\[\d+\]|\^\d+|[①②③④⑤⑥⑦⑧⑨⑩]|\d+)\s+.+$")

    def apply(self, text: str, **kwargs) -> str:
        action = kwargs.get("footnote_action", "remove")

        if action == "keep":
            return text

        lines = text.split("\n")
        result_lines = [line for line in lines if not self._is_footnote_line(line)]
        return "\n".join(result_lines)

    def _is_footnote_line(self, line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False
        if self._FOOTNOTE_LINE_RE.match(stripped):
            return True
        return False


register(ProcessFootnotesRule())
```

- [ ] **Step 4: 注册新规则**

在 `cleaners/rules/__init__.py` 末尾添加：

```python
from . import footnote
```

- [ ] **Step 5: 更新 `app.py` CleanOptions**

在 `filter_page_numbers` 之后添加：

```python
    process_footnotes: bool = False
    footnote_action: str = "remove"
```

- [ ] **Step 6: 运行测试确认通过**

Run: `cd knowledge-process-api && python -m pytest tests/test_footnote_rule.py -v`
Expected: PASS

- [ ] **Step 7: 运行全量测试**

Run: `cd knowledge-process-api && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 8: 提交**

```bash
git add knowledge-process-api/src/fastgpt_demo/cleaners/rules/footnote.py
git add knowledge-process-api/src/fastgpt_demo/cleaners/rules/__init__.py
git add knowledge-process-api/app.py
git add knowledge-process-api/tests/test_footnote_rule.py
git commit -m "feat: add footnote processing rule (process_footnotes)"
```

---

### Task 5: HTML 内容过滤（解析层 + 清洗层）

**Files:**
- Modify: `knowledge-process-api/src/fastgpt_demo/parsers/html_parser.py`
- Modify: `knowledge-process-api/src/fastgpt_demo/parsers/__init__.py`
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/rules/html_clean.py`
- Modify: `knowledge-process-api/src/fastgpt_demo/cleaners/rules/__init__.py`
- Modify: `knowledge-process-api/app.py`
- Test: `knowledge-process-api/tests/test_html_clean_rule.py`
- Test: `knowledge-process-api/tests/test_html_parser_noise.py`

- [ ] **Step 5.1: 写 HTML 解析器噪声移除测试**

```python
# tests/test_html_parser_noise.py
import pytest
from fastgpt_demo.parsers.html_parser import parse


class TestHtmlParserNoiseRemoval:
    def test_removes_script_tags(self):
        html = b"<html><body><script>alert('x')</script><p>content</p></body></html>"
        result = parse(html, remove_noise=True)
        assert "alert" not in result.format_text
        assert "content" in result.format_text

    def test_removes_nav_tags(self):
        html = b"<html><body><nav>menu</nav><p>content</p></body></html>"
        result = parse(html, remove_noise=True)
        assert "menu" not in result.format_text
        assert "content" in result.format_text

    def test_removes_footer_tags(self):
        html = b"<html><body><footer>copyright</footer><p>content</p></body></html>"
        result = parse(html, remove_noise=True)
        assert "copyright" not in result.format_text
        assert "content" in result.format_text

    def test_identifies_article_content(self):
        html = b"<html><body><nav>menu</nav><article><p>main content</p></article></body></html>"
        result = parse(html, remove_noise=True)
        assert "main content" in result.format_text
        assert "menu" not in result.format_text

    def test_no_noise_removal_when_disabled(self):
        html = b"<html><body><nav>menu</nav><p>content</p></body></html>"
        result = parse(html, remove_noise=False)
        assert "menu" in result.format_text

    def test_preserves_raw_text(self):
        html = b"<html><body><nav>menu</nav><p>content</p></body></html>"
        result = parse(html, remove_noise=True)
        assert "menu" in result.raw_text
```

- [ ] **Step 5.2: 运行测试确认失败**

Run: `cd knowledge-process-api && python -m pytest tests/test_html_parser_noise.py -v`
Expected: FAIL — `remove_noise` 参数不存在

- [ ] **Step 5.3: 修改 HTML 解析器**

```python
# src/fastgpt_demo/parsers/html_parser.py
"""HTML parser — 使用 BeautifulSoup 提取文本和结构化内容。"""

from __future__ import annotations

import chardet
from bs4 import BeautifulSoup

from ._types import ParseResult

NOISE_TAGS = ['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']
CONTENT_SELECTORS = ['article', 'main', 'div.content', 'div.article', 'div#content']


def parse(buffer: bytes, remove_noise: bool = True, **kwargs) -> ParseResult:
    """解析 HTML 文件，提取纯文本和结构化 HTML 预览。

    - raw_text: 原始 HTML 内容（供 Markdown 转换器使用，始终保留完整 HTML）
    - format_text: 清洗后的 HTML（移除干扰标签、识别主要内容区域）
    - html_preview: 结构化 HTML 预览
    """

    try:
        html_str = buffer.decode("utf-8")
    except UnicodeDecodeError:
        detection = chardet.detect(buffer)
        fallback_encoding: str = detection.get("encoding") or "utf-8"
        html_str = buffer.decode(fallback_encoding, errors="replace")

    soup = BeautifulSoup(html_str, "html.parser")

    raw_text = str(soup)

    if remove_noise:
        for tag in soup.find_all(NOISE_TAGS):
            tag.decompose()

        main_content = None
        for selector in CONTENT_SELECTORS:
            main_content = soup.select_one(selector)
            if main_content:
                break

        content_soup = main_content if main_content else (soup.body if soup.body else soup)
    else:
        content_soup = soup.body if soup.body else soup

    format_text = str(content_soup)
    html_preview = str(content_soup)

    return ParseResult(
        raw_text=raw_text,
        format_text=format_text,
        html_preview=html_preview,
        image_list=[],
    )
```

- [ ] **Step 5.4: 修改 `parsers/__init__.py` 传递参数**

在 `parse_file` 函数中，将 HTML 解析器调用改为传递 `remove_html_noise` 参数：

找到 `parsers/__init__.py` 中 `dispatch` 字典后的代码，将 HTML 解析器调用从：

```python
    return handler(buffer)
```

改为在 `if parser_key == "pdf":` 块之后添加：

```python
    if parser_key == "html":
        return handler(buffer, remove_noise=kwargs.get("remove_html_noise", True))

    return handler(buffer)
```

同时修改 `parse_file` 函数签名，添加 `remove_html_noise` 参数：

```python
def parse_file(
    buffer: bytes,
    filename: str,
    method: str = "auto",
    engine: str = "fastgpt",
    header_footer_ratio: float = 0.05,
    remove_html_noise: bool = True,
) -> ParseResult:
```

- [ ] **Step 5.5: 运行 HTML 解析器测试**

Run: `cd knowledge-process-api && python -m pytest tests/test_html_parser_noise.py -v`
Expected: PASS

- [ ] **Step 5.6: 写 HTML 清洗规则测试**

```python
# tests/test_html_clean_rule.py
import pytest
from fastgpt_demo.cleaners.registry import get, clear
from fastgpt_demo.cleaners import rules as _rules  # noqa: F401


@pytest.fixture(autouse=True)
def _setup():
    clear()
    from fastgpt_demo.cleaners.rules import html_clean
    yield
    clear()


class TestRemoveHtmlCommentsRule:
    def test_removes_html_comment(self):
        rule = get("remove_html_comments")
        text = "before<!-- comment -->after"
        result = rule.apply(text)
        assert result == "beforeafter"

    def test_removes_multiline_comment(self):
        rule = get("remove_html_comments")
        text = "before<!-- line1\nline2 -->after"
        result = rule.apply(text)
        assert result == "beforeafter"

    def test_preserves_text_without_comments(self):
        rule = get("remove_html_comments")
        text = "普通文本"
        result = rule.apply(text)
        assert result == "普通文本"


class TestNormalizeHtmlEntitiesRule:
    def test_converts_common_entities(self):
        rule = get("normalize_html_entities")
        text = "&amp; &lt; &gt; &quot;"
        result = rule.apply(text)
        assert result == '& < > "'

    def test_converts_nbsp(self):
        rule = get("normalize_html_entities")
        text = "hello&nbsp;world"
        result = rule.apply(text)
        assert result == "hello world"

    def test_converts_decimal_reference(self):
        rule = get("normalize_html_entities")
        text = "&#65;&#66;"
        result = rule.apply(text)
        assert result == "AB"

    def test_converts_hex_reference(self):
        rule = get("normalize_html_entities")
        text = "&#x41;&#x42;"
        result = rule.apply(text)
        assert result == "AB"

    def test_converts_chinese_entities(self):
        rule = get("normalize_html_entities")
        text = "&copy; &reg; &trade;"
        result = rule.apply(text)
        assert result == "© ® ™"


class TestFilterHtmlNoiseRule:
    def test_removes_copyright(self):
        rule = get("filter_html_noise")
        text = "正文内容\ncopyright © 2024 公司名\n更多正文"
        result = rule.apply(text)
        assert "copyright" not in result
        assert "正文内容" in result

    def test_removes_icp(self):
        rule = get("filter_html_noise")
        text = "正文内容\n沪ICP备12345678号\n更多正文"
        result = rule.apply(text)
        assert "沪ICP" not in result

    def test_removes_disclaimer(self):
        rule = get("filter_html_noise")
        text = "正文内容\n免责声明：本文仅供参考\n更多正文"
        result = rule.apply(text)
        assert "免责声明" not in result

    def test_preserves_normal_text(self):
        rule = get("filter_html_noise")
        text = "普通文本没有噪声"
        result = rule.apply(text)
        assert result == "普通文本没有噪声"

    def test_custom_noise_patterns(self):
        rule = get("filter_html_noise")
        text = "正文\n自定义噪声行\n更多正文"
        result = rule.apply(text, html_noise_patterns=[r"自定义噪声.*"])
        assert "自定义噪声行" not in result

    def test_preserves_empty_lines(self):
        rule = get("filter_html_noise")
        text = "正文\n\n更多正文"
        result = rule.apply(text)
        assert "\n\n" in result
```

- [ ] **Step 5.7: 运行测试确认失败**

Run: `cd knowledge-process-api && python -m pytest tests/test_html_clean_rule.py -v`
Expected: FAIL — `html_clean` 模块不存在

- [ ] **Step 5.8: 实现 HTML 清洗规则**

```python
# src/fastgpt_demo/cleaners/rules/html_clean.py
from __future__ import annotations

import re

from ..base import CleanRule
from ..registry import register


class RemoveHtmlCommentsRule(CleanRule):
    name = "remove_html_comments"
    description = "移除 HTML 注释（<!-- ... -->）"
    default_enabled = True

    _COMMENT_RE = re.compile(r"<!--[\s\S]*?-->|<!--[\s\S]*$", re.MULTILINE)

    def apply(self, text: str, **kwargs) -> str:
        return self._COMMENT_RE.sub("", text)


class NormalizeHtmlEntitiesRule(CleanRule):
    name = "normalize_html_entities"
    description = "将 HTML 命名实体和数字引用转换为 Unicode 字符"
    default_enabled = True

    _NAMED_ENTITIES = {
        "&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">",
        "&quot;": '"', "&#39;": "'", "&apos;": "'",
        "&mdash;": "\u2014", "&ndash;": "\u2013", "&hellip;": "\u2026",
        "&copy;": "\u00a9", "&reg;": "\u00ae", "&trade;": "\u2122",
        "&lsquo;": "\u2018", "&rsquo;": "\u2019",
        "&ldquo;": "\u201c", "&rdquo;": "\u201d",
        "&deg;": "\u00b0",
    }
    _DECIMAL_RE = re.compile(r"&#(\d+);")
    _HEX_RE = re.compile(r"&#x([0-9a-fA-F]+);")

    def apply(self, text: str, **kwargs) -> str:
        for entity, char in self._NAMED_ENTITIES.items():
            text = text.replace(entity, char)
        text = self._DECIMAL_RE.sub(lambda m: chr(int(m.group(1))), text)
        text = self._HEX_RE.sub(lambda m: chr(int(m.group(1), 16)), text)
        return text


class FilterHtmlNoiseRule(CleanRule):
    name = "filter_html_noise"
    description = "移除版权声明、备案信息、广告关键词等网页噪声"
    default_enabled = False

    BUILTIN_NOISE_PATTERNS = [
        r"copyright\s*©?\s*\d{4}.*$",
        r"all\s+rights\s+reserved.*$",
        r"[沪京粤深]ICP[备证]\d+号.*$",
        r"免责声明[：:].*$",
        r"本文来源[：:].*$",
        r"责任编辑[：:].*$",
        r"[浏阅]读次数[：:]\s*\d+.*$",
    ]
    BUILTIN_AD_KEYWORDS = ["广告", "推广", "优惠", "促销", "VIP", "购买", "热线"]

    def apply(self, text: str, **kwargs) -> str:
        noise_patterns = kwargs.get("html_noise_patterns", [])
        ad_keywords = kwargs.get("html_ad_keywords", [])

        all_patterns = list(self.BUILTIN_NOISE_PATTERNS) + list(noise_patterns)
        all_ads = list(self.BUILTIN_AD_KEYWORDS) + list(ad_keywords)

        compiled = [re.compile(p, re.IGNORECASE) for p in all_patterns]

        lines = text.split("\n")
        result_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                result_lines.append(line)
                continue

            is_noise = any(p.search(stripped) for p in compiled)

            if not is_noise and all_ads:
                ad_count = sum(1 for kw in all_ads if kw in stripped)
                if ad_count > 0 and ad_count / max(len(stripped), 1) > 0.3:
                    is_noise = True

            if not is_noise:
                result_lines.append(line)

        return "\n".join(result_lines)


register(RemoveHtmlCommentsRule())
register(NormalizeHtmlEntitiesRule())
register(FilterHtmlNoiseRule())
```

- [ ] **Step 5.9: 注册新规则**

在 `cleaners/rules/__init__.py` 末尾添加：

```python
from . import html_clean
```

- [ ] **Step 5.10: 更新 `app.py`**

在 `footnote_action` 之后添加 CleanOptions 新字段：

```python
    remove_html_comments: bool = True
    normalize_html_entities: bool = True
    filter_html_noise: bool = False
    html_noise_patterns: list[str] = []
    html_ad_keywords: list[str] = []
```

在 `/api/parse` 路由中添加 `remove_html_noise` 参数：

```python
@app.post("/api/parse", response_model=ParseResponse)
async def parse(
    file: UploadFile = File(...),
    method: str = Form("auto"),
    engine: str = Form("fastgpt"),
    header_footer_ratio: float = Form(0.05),
    remove_html_noise: bool = Form(True),
):
```

并将 `remove_html_noise` 传递给 `parse_file`：

```python
        result: ParseResult = parse_file(
            buffer, file.filename or "unknown.txt", method, engine,
            header_footer_ratio=header_footer_ratio,
            remove_html_noise=remove_html_noise,
        )
```

- [ ] **Step 5.11: 运行全量测试**

Run: `cd knowledge-process-api && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 5.12: 提交**

```bash
git add knowledge-process-api/src/fastgpt_demo/parsers/html_parser.py
git add knowledge-process-api/src/fastgpt_demo/parsers/__init__.py
git add knowledge-process-api/src/fastgpt_demo/cleaners/rules/html_clean.py
git add knowledge-process-api/src/fastgpt_demo/cleaners/rules/__init__.py
git add knowledge-process-api/app.py
git add knowledge-process-api/tests/test_html_clean_rule.py
git add knowledge-process-api/tests/test_html_parser_noise.py
git commit -m "feat: add HTML content filtering (parser noise removal + 3 clean rules)"
```

---

### Task 6: CleanProfile 预设机制

**Files:**
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/profiles/__init__.py`
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/profiles/base.py`
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/profiles/registry.py`
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/profiles/default.py`
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/profiles/pdf_academic.py`
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/profiles/pdf_business.py`
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/profiles/docx_report.py`
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/profiles/table_data.py`
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/profiles/legal.py`
- Create: `knowledge-process-api/src/fastgpt_demo/cleaners/profiles/web_content.py`
- Modify: `knowledge-process-api/src/fastgpt_demo/cleaners/text_cleaner.py`
- Modify: `knowledge-process-api/src/fastgpt_demo/cleaners/__init__.py`
- Modify: `knowledge-process-api/app.py`
- Test: `knowledge-process-api/tests/test_clean_profile.py`

- [ ] **Step 6.1: 写失败测试**

```python
# tests/test_clean_profile.py
import pytest
from fastgpt_demo.cleaners.profiles.base import CleanProfile
from fastgpt_demo.cleaners.profiles.registry import (
    register_profile, get_profile, get_profile_for_file, clear_profiles,
)


@pytest.fixture(autouse=True)
def _clean():
    clear_profiles()
    yield
    clear_profiles()


class TestCleanProfile:
    def test_to_options_dict(self):
        p = CleanProfile(
            name="test",
            description="test profile",
            rules={"trim": True, "filter_toc": True},
            params={"watermark_min_repeat": 3},
        )
        d = p.to_options_dict()
        assert d["trim"] is True
        assert d["filter_toc"] is True
        assert d["watermark_min_repeat"] == 3

    def test_register_and_get(self):
        p = CleanProfile(name="test", description="test", rules={}, params={})
        register_profile(p)
        assert get_profile("test") is p

    def test_get_profile_for_file_pdf(self):
        p = CleanProfile(name="pdf_academic", description="test", rules={}, params={})
        register_profile(p)
        assert get_profile_for_file("paper.pdf").name == "pdf_academic"

    def test_get_profile_for_file_html(self):
        p = CleanProfile(name="web_content", description="test", rules={}, params={})
        register_profile(p)
        assert get_profile_for_file("page.html").name == "web_content"

    def test_get_profile_for_file_unknown(self):
        assert get_profile_for_file("unknown.xyz") is None

    def test_get_missing_profile(self):
        assert get_profile("nonexistent") is None


class TestBuiltinProfiles:
    def test_default_profile_exists(self):
        from fastgpt_demo.cleaners.profiles import _load_builtins
        _load_builtins()
        p = get_profile("default")
        assert p is not None
        assert p.name == "default"

    def test_pdf_academic_profile(self):
        from fastgpt_demo.cleaners.profiles import _load_builtins
        _load_builtins()
        p = get_profile("pdf_academic")
        assert p is not None
        opts = p.to_options_dict()
        assert opts.get("filter_toc") is True
        assert opts.get("filter_page_numbers") is True

    def test_web_content_profile(self):
        from fastgpt_demo.cleaners.profiles import _load_builtins
        _load_builtins()
        p = get_profile("web_content")
        assert p is not None
        opts = p.to_options_dict()
        assert opts.get("filter_html_noise") is True
```

- [ ] **Step 6.2: 运行测试确认失败**

Run: `cd knowledge-process-api && python -m pytest tests/test_clean_profile.py -v`
Expected: FAIL — `profiles` 模块不存在

- [ ] **Step 6.3: 实现 CleanProfile 基类**

```python
# src/fastgpt_demo/cleaners/profiles/base.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CleanProfile:
    name: str
    description: str
    rules: dict[str, bool] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)

    def to_options_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result.update(self.rules)
        result.update(self.params)
        return result
```

- [ ] **Step 6.4: 实现 Profile 注册表**

```python
# src/fastgpt_demo/cleaners/profiles/registry.py
from __future__ import annotations

from pathlib import PurePosixPath

from .base import CleanProfile

_PROFILE_REGISTRY: dict[str, CleanProfile] = {}

_EXT_PROFILE_MAP: dict[str, str] = {
    ".pdf": "pdf_academic",
    ".docx": "docx_report",
    ".doc": "docx_report",
    ".csv": "table_data",
    ".xlsx": "table_data",
    ".xls": "table_data",
    ".html": "web_content",
    ".htm": "web_content",
}


def register_profile(profile: CleanProfile) -> None:
    _PROFILE_REGISTRY[profile.name] = profile


def get_profile(name: str) -> CleanProfile | None:
    return _PROFILE_REGISTRY.get(name)


def get_profile_for_file(filename: str) -> CleanProfile | None:
    ext = PurePosixPath(filename).suffix.lower()
    profile_name = _EXT_PROFILE_MAP.get(ext)
    if profile_name:
        return get_profile(profile_name)
    return None


def get_all_profiles() -> list[CleanProfile]:
    return list(_PROFILE_REGISTRY.values())


def clear_profiles() -> None:
    _PROFILE_REGISTRY.clear()
```

- [ ] **Step 6.5: 实现各预设配置**

```python
# src/fastgpt_demo/cleaners/profiles/default.py
from __future__ import annotations

from .base import CleanProfile
from .registry import register_profile

DEFAULT_RULES = {
    "trim": True, "normalize_unicode": True, "remove_invisible_chars": True,
    "remove_chinese_space": True, "normalize_newline": True, "fix_hyphenation": True,
    "collapse_whitespace": True, "remove_empty_lines": True,
    "remove_html_comments": True, "normalize_html_entities": True,
    "filter_html_noise": False, "filter_watermark": False,
    "filter_toc": False, "filter_page_numbers": False,
    "process_footnotes": False, "deduplicate_paragraphs": False,
    "clean_table": False, "clean_markdown_links": True,
    "remove_md_escapes": True, "clean_md_structure": True,
    "mask_sensitive": False, "filter_special_chars": False,
}

DEFAULT_PARAMS = {
    "watermark_keywords": [], "watermark_min_repeat": 2, "watermark_max_line_length": 30,
    "dedup_fuzzy": False, "dedup_fuzzy_threshold": 0.9,
    "footnote_action": "remove",
    "html_noise_patterns": [], "html_ad_keywords": [],
}

register_profile(CleanProfile(
    name="default", description="通用文档", rules=DEFAULT_RULES, params=DEFAULT_PARAMS,
))
```

```python
# src/fastgpt_demo/cleaners/profiles/pdf_academic.py
from __future__ import annotations

from .base import CleanProfile
from .registry import register_profile
from .default import DEFAULT_RULES, DEFAULT_PARAMS

RULES = {**DEFAULT_RULES, "filter_toc": True, "filter_page_numbers": True, "process_footnotes": True}
PARAMS = {**DEFAULT_PARAMS, "footnote_action": "keep"}

register_profile(CleanProfile(
    name="pdf_academic", description="学术论文 PDF", rules=RULES, params=PARAMS,
))
```

```python
# src/fastgpt_demo/cleaners/profiles/pdf_business.py
from __future__ import annotations

from .base import CleanProfile
from .registry import register_profile
from .default import DEFAULT_RULES, DEFAULT_PARAMS

RULES = {**DEFAULT_RULES, "filter_watermark": True, "filter_page_numbers": True}

register_profile(CleanProfile(
    name="pdf_business", description="商务 PDF", rules=RULES, params=DEFAULT_PARAMS,
))
```

```python
# src/fastgpt_demo/cleaners/profiles/docx_report.py
from __future__ import annotations

from .base import CleanProfile
from .registry import register_profile
from .default import DEFAULT_RULES, DEFAULT_PARAMS

RULES = {**DEFAULT_RULES, "filter_toc": True, "process_footnotes": True}
PARAMS = {**DEFAULT_PARAMS, "footnote_action": "keep"}

register_profile(CleanProfile(
    name="docx_report", description="DOCX 报告", rules=RULES, params=PARAMS,
))
```

```python
# src/fastgpt_demo/cleaners/profiles/table_data.py
from __future__ import annotations

from .base import CleanProfile
from .registry import register_profile
from .default import DEFAULT_RULES, DEFAULT_PARAMS

RULES = {**DEFAULT_RULES, "clean_table": True}

register_profile(CleanProfile(
    name="table_data", description="表格数据（CSV/XLSX）", rules=RULES, params=DEFAULT_PARAMS,
))
```

```python
# src/fastgpt_demo/cleaners/profiles/legal.py
from __future__ import annotations

from .base import CleanProfile
from .registry import register_profile
from .default import DEFAULT_RULES, DEFAULT_PARAMS

RULES = {**DEFAULT_RULES, "filter_toc": True, "process_footnotes": True}
PARAMS = {**DEFAULT_PARAMS, "footnote_action": "keep"}

register_profile(CleanProfile(
    name="legal", description="法律文书", rules=RULES, params=PARAMS,
))
```

```python
# src/fastgpt_demo/cleaners/profiles/web_content.py
from __future__ import annotations

from .base import CleanProfile
from .registry import register_profile
from .default import DEFAULT_RULES, DEFAULT_PARAMS

RULES = {**DEFAULT_RULES, "filter_watermark": True, "filter_html_noise": True, "clean_markdown_links": True}

register_profile(CleanProfile(
    name="web_content", description="HTML 网页内容", rules=RULES, params=DEFAULT_PARAMS,
))
```

- [ ] **Step 6.6: 实现 `profiles/__init__.py`**

```python
# src/fastgpt_demo/cleaners/profiles/__init__.py
from __future__ import annotations

from .base import CleanProfile
from .registry import (
    register_profile, get_profile, get_profile_for_file,
    get_all_profiles, clear_profiles,
)

_LOADED = False


def _load_builtins() -> None:
    global _LOADED
    if _LOADED:
        return
    from . import default  # noqa: F401
    from . import pdf_academic  # noqa: F401
    from . import pdf_business  # noqa: F401
    from . import docx_report  # noqa: F401
    from . import table_data  # noqa: F401
    from . import legal  # noqa: F401
    from . import web_content  # noqa: F401
    _LOADED = True


_load_builtins()

__all__ = [
    "CleanProfile", "register_profile", "get_profile",
    "get_profile_for_file", "get_all_profiles", "clear_profiles",
    "_load_builtins",
]
```

- [ ] **Step 6.7: 更新 `cleaners/text_cleaner.py`**

在 `text_cleaner.py` 中添加 profile 支持：

```python
"""Text cleaning utilities — delegates to CleanPipeline for rule-based cleaning."""

from __future__ import annotations

from fastgpt_demo.converters.markdown_converter import (
    fastgpt_simple_text,
    simple_markdown_text,
)
from fastgpt_demo.cleaners.pipeline import CleanPipeline
from fastgpt_demo.cleaners import rules as _rules  # noqa: F401 — trigger registration
from fastgpt_demo.cleaners.profiles import get_profile  # noqa: F401

_pipeline = CleanPipeline()


def simple_text(text: str, options: dict | None = None, profile: str = "default") -> str:
    opts = options or {}
    if not opts and profile != "default":
        p = get_profile(profile)
        if p:
            opts = p.to_options_dict()
    return _pipeline.execute(text, opts)


clean_text = simple_text

__all__ = ["clean_text", "fastgpt_simple_text", "simple_markdown_text", "simple_text"]
```

- [ ] **Step 6.8: 更新 `cleaners/__init__.py`**

```python
from .text_cleaner import clean_text, fastgpt_simple_text, simple_markdown_text, simple_text
from .profiles import get_profile, get_profile_for_file, get_all_profiles

__all__ = ["clean_text", "fastgpt_simple_text", "simple_markdown_text", "simple_text",
           "get_profile", "get_profile_for_file", "get_all_profiles"]
```

- [ ] **Step 6.9: 更新 `app.py` CleanRequest**

在 `CleanRequest` 中添加 `profile` 字段，并修改 `/api/clean` 路由：

```python
class CleanRequest(BaseModel):
    text: str
    options: CleanOptions = Field(default_factory=CleanOptions)
    profile: str = "default"
```

修改 `clean` 路由：

```python
@app.post("/api/clean", response_model=CleanResponse)
async def clean(req: CleanRequest):
    """Clean text with configurable options."""
    try:
        from fastgpt_demo.cleaners.profiles import get_profile as _get_profile
        opts = req.options.model_dump()
        default_opts = CleanOptions().model_dump()
        if opts == default_opts and req.profile != "default":
            p = _get_profile(req.profile)
            if p:
                opts = p.to_options_dict()
        cleaned = clean_text(req.text, opts)
        return CleanResponse(cleaned=cleaned)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Clean failed: {exc}") from exc
```

- [ ] **Step 6.10: 运行测试**

Run: `cd knowledge-process-api && python -m pytest tests/test_clean_profile.py -v`
Expected: PASS

- [ ] **Step 6.11: 运行全量测试**

Run: `cd knowledge-process-api && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 6.12: 提交**

```bash
git add knowledge-process-api/src/fastgpt_demo/cleaners/profiles/
git add knowledge-process-api/src/fastgpt_demo/cleaners/text_cleaner.py
git add knowledge-process-api/src/fastgpt_demo/cleaners/__init__.py
git add knowledge-process-api/app.py
git add knowledge-process-api/tests/test_clean_profile.py
git commit -m "feat: add CleanProfile preset mechanism (7 built-in profiles)"
```

---

### Task 7: 清洗与转换解耦

**Files:**
- Modify: `knowledge-process-api/src/fastgpt_demo/converters/markdown_converter.py`

- [ ] **Step 7.1: 写回归测试**

```python
# tests/test_markdown_converter_delegate.py
import pytest
from fastgpt_demo.converters.markdown_converter import (
    fastgpt_simple_text, simple_markdown_text,
)
from fastgpt_demo.cleaners.text_cleaner import simple_text


class TestSimpleTextDelegate:
    def test_simple_text_matches_pipeline(self):
        text = "  hello  world  \r\n\r\n\r\n  "
        result_converter = fastgpt_simple_text(text)
        result_pipeline = simple_text(text)
        assert result_converter == result_pipeline

    def test_simple_markdown_text_produces_output(self):
        text = "# 标题\n\n[链接\n文本](url)\n\n\\*转义\\*"
        result = simple_markdown_text(text)
        assert "标题" in result
        assert "\\*" not in result


class TestBackwardCompatibility:
    def test_fastgpt_simple_text_basic(self):
        text = "  hello  world  \n\n\n  "
        result = fastgpt_simple_text(text)
        assert result == "hello world"

    def test_simple_markdown_text_link(self):
        text = "[hello\nworld](http://example.com)"
        result = simple_markdown_text(text)
        assert "[helloworld](http://example.com)" in result
```

- [ ] **Step 7.2: 运行回归测试确认当前行为**

Run: `cd knowledge-process-api && python -m pytest tests/test_markdown_converter_delegate.py -v`
Expected: PASS（当前行为应与 pipeline 一致）

- [ ] **Step 7.3: 修改 `markdown_converter.py`**

将 `simple_text()` 函数改为委托 `cleaners.text_cleaner.simple_text()`，同时保留 `fastgpt_simple_text()` 和 `simple_markdown_text()` 不变：

在 `markdown_converter.py` 中，将 `simple_text()` 函数替换为：

```python
def simple_text(text: str, options: dict | None = None) -> str:
    """
    Interactive text cleaning — delegates to CleanPipeline.
    保留此函数作为向后兼容入口。
    """
    from fastgpt_demo.cleaners.text_cleaner import simple_text as _pipeline_simple
    return _pipeline_simple(text, options)
```

删除 `_DEFAULT_OPTIONS` 字典（已不再需要）。

- [ ] **Step 7.4: 运行回归测试**

Run: `cd knowledge-process-api && python -m pytest tests/test_markdown_converter_delegate.py tests/test_clean_pipeline.py -v`
Expected: ALL PASS

- [ ] **Step 7.5: 运行全量测试**

Run: `cd knowledge-process-api && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 7.6: 提交**

```bash
git add knowledge-process-api/src/fastgpt_demo/converters/markdown_converter.py
git add knowledge-process-api/tests/test_markdown_converter_delegate.py
git commit -m "refactor: delegate simple_text() to CleanPipeline, remove duplicate logic"
```

---

### Task 8: 前端 UI 更新

**Files:**
- Modify: `apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue`

- [ ] **Step 8.1: 阅读 Vue 文件了解当前结构**

先通读 `KnowledgeProcessDemo.vue`，理解：
- `cleanOptions` 的响应式定义
- 清洗选项 UI 的布局
- API 调用逻辑

- [ ] **Step 8.2: 添加 CleanProfile 预设常量和选择器**

在 `<script setup>` 中添加：

```js
const CLEAN_PROFILES = {
  default: { label: '默认', options: { trim: true, normalize_unicode: true, remove_invisible_chars: true, remove_chinese_space: true, normalize_newline: true, fix_hyphenation: true, collapse_whitespace: true, remove_empty_lines: true, remove_html_comments: true, normalize_html_entities: true, filter_html_noise: false, filter_watermark: false, filter_toc: false, filter_page_numbers: false, process_footnotes: false, footnote_action: 'remove', deduplicate_paragraphs: false, clean_table: false, clean_markdown_links: true, remove_md_escapes: true, clean_md_structure: true, mask_sensitive: false, filter_special_chars: false } },
  pdf_academic: { label: '学术论文 PDF', options: { trim: true, normalize_unicode: true, remove_invisible_chars: true, remove_chinese_space: true, normalize_newline: true, fix_hyphenation: true, collapse_whitespace: true, remove_empty_lines: true, remove_html_comments: true, normalize_html_entities: true, filter_html_noise: false, filter_watermark: false, filter_toc: true, filter_page_numbers: true, process_footnotes: true, footnote_action: 'keep', deduplicate_paragraphs: false, clean_table: false, clean_markdown_links: true, remove_md_escapes: true, clean_md_structure: true, mask_sensitive: false, filter_special_chars: false } },
  pdf_business: { label: '商务 PDF', options: { trim: true, normalize_unicode: true, remove_invisible_chars: true, remove_chinese_space: true, normalize_newline: true, fix_hyphenation: true, collapse_whitespace: true, remove_empty_lines: true, remove_html_comments: true, normalize_html_entities: true, filter_html_noise: false, filter_watermark: true, filter_toc: false, filter_page_numbers: true, process_footnotes: false, footnote_action: 'remove', deduplicate_paragraphs: false, clean_table: false, clean_markdown_links: true, remove_md_escapes: true, clean_md_structure: true, mask_sensitive: false, filter_special_chars: false } },
  docx_report: { label: 'DOCX 报告', options: { trim: true, normalize_unicode: true, remove_invisible_chars: true, remove_chinese_space: true, normalize_newline: true, fix_hyphenation: true, collapse_whitespace: true, remove_empty_lines: true, remove_html_comments: true, normalize_html_entities: true, filter_html_noise: false, filter_watermark: false, filter_toc: true, filter_page_numbers: false, process_footnotes: true, footnote_action: 'keep', deduplicate_paragraphs: false, clean_table: false, clean_markdown_links: true, remove_md_escapes: true, clean_md_structure: true, mask_sensitive: false, filter_special_chars: false } },
  table_data: { label: '表格数据', options: { trim: true, normalize_unicode: true, remove_invisible_chars: true, remove_chinese_space: true, normalize_newline: true, fix_hyphenation: true, collapse_whitespace: true, remove_empty_lines: true, remove_html_comments: true, normalize_html_entities: true, filter_html_noise: false, filter_watermark: false, filter_toc: false, filter_page_numbers: false, process_footnotes: false, footnote_action: 'remove', deduplicate_paragraphs: false, clean_table: true, clean_markdown_links: true, remove_md_escapes: true, clean_md_structure: true, mask_sensitive: false, filter_special_chars: false } },
  legal: { label: '法律文书', options: { trim: true, normalize_unicode: true, remove_invisible_chars: true, remove_chinese_space: true, normalize_newline: true, fix_hyphenation: true, collapse_whitespace: true, remove_empty_lines: true, remove_html_comments: true, normalize_html_entities: true, filter_html_noise: false, filter_watermark: false, filter_toc: true, filter_page_numbers: false, process_footnotes: true, footnote_action: 'keep', deduplicate_paragraphs: false, clean_table: false, clean_markdown_links: true, remove_md_escapes: true, clean_md_structure: true, mask_sensitive: false, filter_special_chars: false } },
  web_content: { label: '网页内容', options: { trim: true, normalize_unicode: true, remove_invisible_chars: true, remove_chinese_space: true, normalize_newline: true, fix_hyphenation: true, collapse_whitespace: true, remove_empty_lines: true, remove_html_comments: true, normalize_html_entities: true, filter_html_noise: true, filter_watermark: true, filter_toc: false, filter_page_numbers: false, process_footnotes: false, footnote_action: 'remove', deduplicate_paragraphs: false, clean_table: false, clean_markdown_links: true, remove_md_escapes: true, clean_md_structure: true, mask_sensitive: false, filter_special_chars: false } },
  custom: { label: '自定义', options: null },
}

const selectedProfile = ref('default')

function applyProfile(profileName) {
  const profile = CLEAN_PROFILES[profileName]
  if (profile && profile.options) {
    Object.assign(cleanOptions.value, JSON.parse(JSON.stringify(profile.options)))
    selectedProfile.value = profileName
  }
}

function isOptionsEqual(a, b) {
  if (!b) return false
  return Object.keys(b).every(key => a[key] === b[key])
}
```

- [ ] **Step 8.3: 添加 watch 监听手动修改**

```js
watch(cleanOptions, (newVal) => {
  const currentProfile = CLEAN_PROFILES[selectedProfile.value]
  if (currentProfile && currentProfile.options && !isOptionsEqual(newVal, currentProfile.options)) {
    selectedProfile.value = 'custom'
  }
}, { deep: true })
```

- [ ] **Step 8.4: 在模板中添加预设选择器和 P2 规则控件**

在清洗选项区域的顶部添加预设选择器，在现有规则列表中添加 P2 新增规则的 checkbox 控件。

- [ ] **Step 8.5: 验证前端构建**

Run: `cd apps/knowledge-process-demo && npm run build`
Expected: BUILD SUCCESS

- [ ] **Step 8.6: 提交**

```bash
git add apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue
git commit -m "feat: add CleanProfile selector and P2 rule controls to demo UI"
```

---

### Task 9: 集成测试和回归验证

**Files:**
- All test files

- [ ] **Step 9.1: 运行完整后端测试套件**

Run: `cd knowledge-process-api && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 9.2: 验证 CleanProfile 预设正确加载**

```python
# 手动验证
from fastgpt_demo.cleaners.profiles import get_profile, get_all_profiles
for p in get_all_profiles():
    print(f"{p.name}: {p.description}")
    opts = p.to_options_dict()
    enabled = [k for k, v in opts.items() if v is True]
    print(f"  启用: {enabled}")
```

- [ ] **Step 9.3: 验证 `/api/clean` 端点 profile 参数**

```bash
# 默认 profile
curl -X POST http://localhost:8000/api/clean -H "Content-Type: application/json" -d '{"text": "  hello  world  "}'

# 指定 profile
curl -X POST http://localhost:8000/api/clean -H "Content-Type: application/json" -d '{"text": "1.1 概述 .... 12\n1.2 背景 .... 15\n1.3 方法 .... 20\n正文内容", "profile": "pdf_academic"}'
```

- [ ] **Step 9.4: 验证 `/api/parse` 端点 remove_html_noise 参数**

```bash
curl -X POST http://localhost:8000/api/parse -F "file=@test.html" -F "remove_html_noise=true"
```

- [ ] **Step 9.5: 验证前端 Demo 全流程**

启动前端开发服务器，测试：
1. 选择预设 → 规则自动填充
2. 手动修改规则 → 预设切换为「自定义」
3. 上传 HTML 文件 → 验证噪声移除
4. 清洗文本 → 验证新规则生效

- [ ] **Step 9.6: 最终提交**

```bash
git commit --allow-empty -m "chore: P2 data cleaning rules implementation complete"
```
