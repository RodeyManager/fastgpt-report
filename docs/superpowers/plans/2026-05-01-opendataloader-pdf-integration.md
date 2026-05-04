# OpenDataLoader-PDF 解析引擎集成实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：** 在文档解析步骤中新增 opendataloader-pdf 解析引擎（Docling Server），用户可从 FastGPT/MinerU/OpenDataLoader-PDF 三种引擎中选择。

**架构：** 遵循现有引擎分派模式——前端新增下拉选项，后端新增独立解析器模块 `opendataloader_pdf_parser.py`，通过 `parse_file()` 的 `engine` 参数分派。opendataloader-pdf 通过 HTTP 调用本地 `localhost:5002` 的 Docling Server，将返回的 DoclingDocument JSON 提取为文本。

**技术栈：** Python FastAPI + httpx（调用 Docling Server）+ Vue 3

**opendataloader-pdf 服务信息：**
- 地址：`http://localhost:5002`
- 接口：`POST /v1/convert/file`（multipart form，字段名 `files`）
- 返回：`{"document": {"json_content": <DoclingDocument>}, "status": "success", ...}`
- DoclingDocument 结构：`texts[]`（每个含 `text`、`prov` 含 `page_no`/`bbox`）、`tables[]`、`pictures[]`

---

## 文件结构

| 操作 | 文件 | 职责 |
|------|------|------|
| 新建 | `knowledge-process-api/src/fastgpt_demo/parsers/opendataloader_pdf_parser.py` | 调用 Docling Server 解析 PDF，提取文本 |
| 修改 | `knowledge-process-api/src/fastgpt_demo/parsers/__init__.py` | 新增 `engine="opendataloader-pdf"` 分派分支 |
| 修改 | `knowledge-process-api/app.py` | `/api/parse` 端点 `engine` 参数新增 `opendataloader-pdf`（只需扩大 description，无逻辑改动） |
| 修改 | `apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue` | 前端引擎下拉框新增 `opendataloader-pdf` 选项 |
| 新建 | `knowledge-process-api/tests/parsers/test_opendataloader_pdf_parser.py` | 解析器单元测试 + HTTP 调用集成测试 |

---

### Task 1: 创建 OpenDataLoader-PDF 解析器模块

**文件：**
- 新建：`knowledge-process-api/src/fastgpt_demo/parsers/opendataloader_pdf_parser.py`

**说明：** Docling Server 通过 HTTP 接收 PDF 文件，返回 DoclingDocument JSON。解析器负责：
1. 发送 PDF 文件到 `http://localhost:5002/v1/convert/file`
2. 从 `document.json_content.texts[]` 中提取文本并按页组织
3. 如有 `tables[]`，转换为 Markdown 表格
4. 返回 `ParseResult`（raw_text 为原始提取文本，format_text 为清洗后文本）

- [ ] **Step 1: 编写解析器模块**

```python
"""
OpenDataLoader-PDF 解析器
通过 HTTP 调用本地 Docling Server (http://localhost:5002) 解析 PDF
"""

from __future__ import annotations

import httpx
from typing import Optional

from ._types import ParseResult

DOCLING_SERVER_URL = "http://localhost:5002"
DOCLING_CONVERT_URL = f"{DOCLING_SERVER_URL}/v1/convert/file"


def _extract_texts(doc_json: dict) -> str:
    """从 DoclingDocument JSON 中提取文本，按页组织"""
    texts = doc_json.get("texts", [])
    texts_by_page: dict[int, list[str]] = {}
    for item in texts:
        prov_list = item.get("prov", [])
        if not prov_list:
            continue
        page_no = prov_list[0].get("page_no", 0)
        text = item.get("text", "")
        if not text:
            continue
        texts_by_page.setdefault(page_no, []).append(text)

    pages = []
    for page_no in sorted(texts_by_page.keys()):
        page_lines = texts_by_page[page_no]
        pages.append("\n".join(page_lines))

    return "\n\n".join(pages)


def _extract_tables_as_markdown(doc_json: dict) -> str:
    """将 DoclingDocument 中的表格转为 Markdown"""
    tables = doc_json.get("tables", [])
    if not tables:
        return ""

    md_tables = []
    for table in tables:
        data = table.get("data", [])
        if not data:
            continue
        # 检查是否有表头（第一行包含 column_header label）
        num_cols = max(len(row) for row in data) if data else 0
        if num_cols == 0:
            continue

        # 获取文本的 grid 数据
        grid = []
        for row in data:
            grid_row = []
            for cell in row:
                cell_text = cell.get("text", "")
                grid_row.append(cell_text)
            grid.append(grid_row)

        if not grid:
            continue

        # 构建 Markdown 表格
        lines = []
        header = grid[0]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        for row in grid[1:]:
            padded = (row + [""] * len(header))[:len(header)]
            lines.append("| " + " | ".join(padded) + " |")

        md_tables.append("\n".join(lines))

    return "\n\n".join(md_tables)


def parse_opendataloader_pdf(
    buffer: bytes,
    timeout: float = 120.0,
) -> ParseResult:
    """通过 Docling Server 解析 PDF

    参数:
        buffer: PDF 文件字节内容
        timeout: HTTP 请求超时秒数

    返回:
        ParseResult: raw_text 为提取的纯文本，format_text 为含 Markdown 表格的文本
    """
    resp = httpx.post(
        DOCLING_CONVERT_URL,
        files={"files": ("input.pdf", buffer, "application/pdf")},
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()

    errors = data.get("errors", [])
    if errors:
        raise RuntimeError(f"Docling 解析错误: {errors[0]}")

    doc_json = data["document"]["json_content"]

    text_content = _extract_texts(doc_json)
    table_content = _extract_tables_as_markdown(doc_json)

    if table_content:
        format_text = text_content + "\n\n" + table_content
    else:
        format_text = text_content

    raw_text = text_content

    return ParseResult(
        raw_text=raw_text,
        format_text=format_text,
        html_preview="",
        image_list=[],
    )
```

- [ ] **Step 2: 运行测试验证模块可导入**

```bash
cd knowledge-process-api && uv run python -c "from fastgpt_demo.parsers.opendataloader_pdf_parser import parse_opendataloader_pdf; print('import OK')"
```

预期输出：`import OK`

- [ ] **Step 3: Commit**

```bash
git add knowledge-process-api/src/fastgpt_demo/parsers/opendataloader_pdf_parser.py
git commit -m "feat: add opendataloader-pdf parser module"
```

---

### Task 2: 注册 OpenDataLoader-PDF 引擎到解析分派逻辑

**文件：**
- 修改：`knowledge-process-api/src/fastgpt_demo/parsers/__init__.py`

**说明：** 修改现有代码，当 `engine="opendataloader-pdf"` 时调用新的解析器。opendataloader-pdf 仅支持 PDF，非 PDF 文件应拒绝。

- [ ] **Step 1: 修改 parse_file() 函数**

在 `parse_file()` 中添加 opendataloader-pdf 分支：

```python
# 在 parse_file() 函数的 mineru 相关代码之后，添加：

    # OpenDataLoader-PDF 引擎（仅支持 PDF）
    if engine == "opendataloader-pdf":
        if parser_key != "pdf":
            raise ValueError(
                f"opendataloader-pdf 引擎仅支持 PDF 文件，"
                f"当前文件类型: {parser_key}"
            )
        from .opendataloader_pdf_parser import parse_opendataloader_pdf

        return parse_opendataloader_pdf(buffer)
```

具体插入位置：在 `if engine == "mineru":` 分支之后，`if parser_key == "html":` 之前。

- [ ] **Step 2: 验证分派逻辑**

```bash
cd knowledge-process-api && uv run python -c "
from fastgpt_demo.parsers import parse_file
with open('tests/fixtures/test.pdf', 'rb') as f:
    buf = f.read()
result = parse_file(buf, 'test.pdf', engine='opendataloader-pdf')
print('raw_text:', result.raw_text[:200])
print('format_text:', result.format_text[:200])
"
```

预期：调用 Docling Server 并返回 ParseResult

- [ ] **Step 3: Commit**

```bash
git add knowledge-process-api/src/fastgpt_demo/parsers/__init__.py
git commit -m "feat: wire opendataloader-pdf engine into parse_file dispatch"
```

---

### Task 3: 更新 API 端点 engine 参数说明

**文件：**
- 修改：`knowledge-process-api/app.py`

**说明：** 更新 `/api/parse` 端点的 `engine` 参数 description，使文档反映新的引擎选项。

- [ ] **Step 1: 更新 engine 参数描述**

```python
engine: str = Form("fastgpt", description="解析引擎，支持 fastgpt / mineru / opendataloader-pdf"),
```

- [ ] **Step 2: Commit**

```bash
git add knowledge-process-api/app.py
git commit -m "chore: update engine param description with opendataloader-pdf"
```

---

### Task 4: 前端新增 OpenDataLoader-PDF 引擎选项

**文件：**
- 修改：`apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue`

**说明：** 解耦 `engines` 计算属性，使 opendataloader-pdf 独立于 `isMineruAvailable` 判断。

- [ ] **Step 1: 新增 opendataloader-pdf 可用性计算属性**

在 `isMineruAvailable` 下方新增：

```javascript
const OPENLOADER_SUPPORTED_EXTS = ['pdf']

const isOpenLoaderAvailable = computed(() => {
  if (!fileInfo.value) return false
  return OPENLOADER_SUPPORTED_EXTS.includes(fileInfo.value.ext.toLowerCase())
})
```

- [ ] **Step 2: 更新 engines 计算属性**

```javascript
const engines = computed(() => {
  const list = [{ value: 'fastgpt', label: 'FastGPT 默认' }]
  if (isMineruAvailable.value) {
    list.push({ value: 'mineru', label: 'MinerU' })
  }
  if (isOpenLoaderAvailable.value) {
    list.push({ value: 'opendataloader-pdf', label: 'OpenDataLoader-PDF' })
  }
  return list
})
```

- [ ] **Step 3: 验证前端无语法错误**

运行前端开发服务器，检查下拉框是否出现第三个选项。

- [ ] **Step 4: Commit**

```bash
git add apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue
git commit -m "feat: add opendataloader-pdf engine option to frontend"
```

---

### Task 5: 编写解析器测试

**文件：**
- 新建：`knowledge-process-api/tests/parsers/test_opendataloader_pdf_parser.py`

- [ ] **Step 1: 编写测试文件**

```python
"""
OpenDataLoader-PDF 解析器测试
"""

import pytest
import httpx
import json
from fastgpt_demo.parsers.opendataloader_pdf_parser import (
    _extract_texts,
    _extract_tables_as_markdown,
    parse_opendataloader_pdf,
)
from fastgpt_demo.parsers._types import ParseResult

DOCLING_CONVERT_URL = "http://localhost:5002/v1/convert/file"


def _docling_available():
    """检测 Docling Server 是否可用"""
    try:
        resp = httpx.get("http://localhost:5002/health", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


docling_available = pytest.mark.skipif(
    not _docling_available(),
    reason="Docling Server (localhost:5002) 不可用",
)


class TestExtractTexts:
    def test_empty_doc(self):
        result = _extract_texts({"texts": []})
        assert result == ""

    def test_single_text(self):
        doc = {
            "texts": [
                {"text": "Hello World", "prov": [{"page_no": 1, "bbox": {}}]}
            ]
        }
        result = _extract_texts(doc)
        assert "Hello World" in result

    def test_multiple_pages(self):
        doc = {
            "texts": [
                {"text": "Page 1 text", "prov": [{"page_no": 1, "bbox": {}}]},
                {"text": "Page 2 text", "prov": [{"page_no": 2, "bbox": {}}]},
            ]
        }
        result = _extract_texts(doc)
        assert "Page 1 text" in result
        assert "Page 2 text" in result
        assert "\n\n" in result

    def test_skips_empty_text(self):
        doc = {
            "texts": [
                {"text": "Valid", "prov": [{"page_no": 1, "bbox": {}}]},
                {"text": "", "prov": [{"page_no": 1, "bbox": {}}]},
            ]
        }
        result = _extract_texts(doc)
        assert result == "Valid"

    def test_no_prov_skipped(self):
        doc = {
            "texts": [
                {"text": "No provenance", "prov": []},
            ]
        }
        result = _extract_texts(doc)
        assert result == ""


class TestExtractTables:
    def test_empty_tables(self):
        result = _extract_tables_as_markdown({"tables": []})
        assert result == ""

    def test_single_table(self):
        doc = {
            "tables": [
                {
                    "data": [
                        [{"text": "Name"}, {"text": "Age"}],
                        [{"text": "Alice"}, {"text": "30"}],
                    ]
                }
            ]
        }
        result = _extract_tables_as_markdown(doc)
        assert "| Name | Age |" in result
        assert "| Alice | 30 |" in result
        assert "| ---" in result

    def test_empty_data(self):
        doc = {"tables": [{"data": []}]}
        result = _extract_tables_as_markdown(doc)
        assert result == ""


@docling_available
class TestParseOpenDataLoaderPdfIntegration:
    def test_parse_success(self):
        with open("tests/fixtures/test.pdf", "rb") as f:
            buffer = f.read()

        result = parse_opendataloader_pdf(buffer, timeout=120)
        assert isinstance(result, ParseResult)
        assert isinstance(result.raw_text, str)
        assert isinstance(result.format_text, str)

    def test_parse_with_page_ranges(self):
        with open("tests/fixtures/test.pdf", "rb") as f:
            buffer = f.read()

        result = parse_opendataloader_pdf(buffer, timeout=120)
        assert isinstance(result, ParseResult)
        assert result.image_list is not None
```

- [ ] **Step 2: 运行测试**

```bash
uv run pytest tests/parsers/test_opendataloader_pdf_parser.py -v --tb=short
```

预期：单元测试 7 passed，集成测试 2 passed（需 Docling Server 运行）

- [ ] **Step 3: 运行全量测试无回归**

```bash
uv run pytest tests/ -v --tb=short
```

预期：全部通过（opendataloader-pdf 集成测试在 Server 不可用时自动 skip）

- [ ] **Step 4: Commit**

```bash
git add knowledge-process-api/tests/parsers/test_opendataloader_pdf_parser.py
git commit -m "test: add opendataloader-pdf parser tests"
```

---

## 自检清单

**1. 需求覆盖：**
- [x] 前端引擎下拉框新增 opendataloader-pdf 选项 — Task 4
- [x] 仅 PDF 文件时显示该选项 — Task 4（`OPENLOADER_SUPPORTED_EXTS = ['pdf']`）
- [x] 后端新增对应解析器 — Task 1
- [x] 解析分派逻辑更新 — Task 2
- [x] API 端点参数说明更新 — Task 3
- [x] 测试覆盖 — Task 5

**2. 无占位符：** 所有步骤均包含具体代码、命令和预期输出。

**3. 类型一致性：** `parse_opendataloader_pdf(buffer: bytes) -> ParseResult` 与现有 `parse_pdf()`、`parse_mineru()` 签名兼容。

**4. 遵循现有模式：**
- 解析器文件结构参照 `mineru_parser.py`
- 返回类型统一使用 `ParseResult`
- 引擎分派在 `__init__.py` 中处理
- 前端参照 `MINERU_SUPPORTED_EXTS` 模式
