# P1 数据清洗结构级优化 — 实施规范文档

> **项目**: fastgpt-report / knowledge-process-api
> **日期**: 2026-04-30
> **优先级**: P1（短期目标）
> **目标**: 引入文档结构感知的清洗能力，实现水印过滤、段落去重、表格清洗、脱敏增强，同时建立 CleanRule 规则化架构

***

## 1. 概述

### 1.1 P1 优化项总览

| 序号 | P1 项 | 实现难度 | 业务价值 | 默认启用 |
|------|-------|---------|---------|---------|
| P1-1 | CleanRule 基类和注册机制 | 🟡 中 | 🟠 高 | — |
| P1-2 | 水印文本过滤 | 🟢 低 | 🟠 高 | ❌ |
| P1-3 | 重复段落去重 | 🟡 中 | 🟠 高 | ❌ |
| P1-4 | 表格清洗（空行空列、表头识别） | 🟡 中 | 🟠 高 | ❌ |
| P1-5 | 敏感信息脱敏增强（银行卡号、护照号） | 🟢 低 | 🟡 中 | ❌ |

### 1.2 设计原则

1. **规则即插件**：每条清洗规则是独立的 `CleanRule` 实例，可独立启用/禁用
2. **配置驱动**：通过 `CleanOptions` 控制规则组合和参数
3. **管道执行**：`CleanPipeline` 按配置顺序执行规则链
4. **向后兼容**：保留 `clean_text()` / `simple_text()` 等现有 API 不变
5. **渐进重构**：先建立规则化架构，再将现有清洗逻辑逐步迁移

### 1.3 规则执行顺序（P1 完成后）

```
trim → normalize_unicode → remove_invisible_chars → remove_chinese_space
→ normalize_newline → fix_hyphenation → collapse_whitespace → remove_empty_lines
→ filter_watermark → deduplicate_paragraphs → clean_table
→ mask_sensitive → filter_special_chars → 控制字符替换
```

***

## 2. 架构设计

### 2.1 目标目录结构

```
cleaners/
├── __init__.py              # 模块导出（更新）
├── text_cleaner.py          # 向后兼容入口（保留，内部改为调用 pipeline）
├── base.py                  # CleanRule 基类 + CleanPipeline
├── registry.py              # 规则注册表
├── rules/
│   ├── __init__.py          # 规则模块导出
│   ├── whitespace.py        # 空白/换行相关规则（从 markdown_converter 迁移）
│   ├── control_chars.py     # 控制字符规则（从 markdown_converter 迁移）
│   ├── chinese_text.py      # 中文文本规则（从 markdown_converter 迁移）
│   ├── hyphenation.py       # 连字符断行修复（从 markdown_converter 迁移）
│   ├── unicode.py           # Unicode 标准化 + 不可见字符（从 markdown_converter 迁移）
│   ├── sensitive.py         # 敏感信息脱敏（从 markdown_converter 迁移 + 增强）
│   ├── special_chars.py     # 特殊字符过滤（从 markdown_converter 迁移）
│   ├── watermark.py         # 水印过滤（新增）
│   ├── deduplication.py     # 重复段落去重（新增）
│   └── table_clean.py       # 表格清洗（新增）
└── pipeline.py              # 清洗管道（按配置执行规则链）
```

### 2.2 CleanRule 基类

```python
# cleaners/base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class CleanRule(ABC):
    """清洗规则基类。每条规则是独立的、可插拔的清洗单元。"""

    name: str = ""           # 规则唯一标识（对应 CleanOptions 中的字段名）
    description: str = ""    # 规则描述
    default_enabled: bool = True  # 默认是否启用

    @abstractmethod
    def apply(self, text: str, **kwargs) -> str:
        """执行清洗规则，返回清洗后的文本。"""
        ...

    def should_run(self, options: dict) -> bool:
        """根据 options 判断本规则是否应执行。"""
        return options.get(self.name, self.default_enabled)
```

### 2.3 CleanPipeline

```python
# cleaners/pipeline.py
from __future__ import annotations
from .base import CleanRule
from .registry import get_all_rules

class CleanPipeline:
    """清洗管道：按注册顺序执行规则链。"""

    def __init__(self, rules: list[CleanRule] | None = None):
        self.rules: list[CleanRule] = rules or get_all_rules()

    def execute(self, text: str, options: dict | None = None) -> str:
        opts = options or {}
        for rule in self.rules:
            if rule.should_run(opts):
                text = rule.apply(text)
        # 始终执行控制字符替换
        text = _replace_control_chars(text)
        return text
```

### 2.4 规则注册表

```python
# cleaners/registry.py
from __future__ import annotations
from .base import CleanRule

_REGISTRY: dict[str, CleanRule] = {}

def register(rule: CleanRule) -> None:
    _REGISTRY[rule.name] = rule

def get(name: str) -> CleanRule:
    return _REGISTRY[name]

def get_all_rules() -> list[CleanRule]:
    return list(_REGISTRY.values())
```

### 2.5 向后兼容策略

- `text_cleaner.py` 保留为入口，内部改为调用 `CleanPipeline.execute()`
- `simple_text()` 函数签名不变，内部委托给 pipeline
- `fastgpt_simple_text()` 和 `simple_markdown_text()` 保持不变（它们是固定规则集的快捷方式）
- `markdown_converter.py` 中的清洗函数保留，但核心逻辑迁移到 `cleaners/rules/` 下

***

## 3. 详细设计

### 3.1 P1-1：CleanRule 基类和注册机制

**目标**：建立规则化架构，使清洗规则可插拔、可配置、可扩展。

**新增文件**：

| 文件 | 职责 |
|------|------|
| `cleaners/base.py` | `CleanRule` 基类定义 |
| `cleaners/registry.py` | 规则注册表（`register`, `get`, `get_all_rules`） |
| `cleaners/pipeline.py` | `CleanPipeline` 管道执行器 |
| `cleaners/rules/__init__.py` | 规则模块导出 + 自动注册 |

**迁移文件**（将 `markdown_converter.py` 中的清洗逻辑拆分为独立规则文件）：

| 文件 | 迁移的规则 |
|------|----------|
| `cleaners/rules/whitespace.py` | `TrimRule`, `CollapseWhitespaceRule`, `RemoveEmptyLinesRule`, `NormalizeNewlineRule` |
| `cleaners/rules/unicode.py` | `NormalizeUnicodeRule`, `RemoveInvisibleCharsRule` |
| `cleaners/rules/chinese_text.py` | `RemoveChineseSpaceRule` |
| `cleaners/rules/hyphenation.py` | `FixHyphenationRule` |
| `cleaners/rules/sensitive.py` | `MaskSensitiveRule`（含增强） |
| `cleaners/rules/special_chars.py` | `FilterSpecialCharsRule` |
| `cleaners/rules/control_chars.py` | 控制字符替换（始终执行，不作为可开关规则） |

**修改文件**：

| 文件 | 修改内容 |
|------|---------|
| `cleaners/text_cleaner.py` | `simple_text()` 内部改为调用 `CleanPipeline.execute()` |
| `cleaners/__init__.py` | 导出新增模块 |
| `converters/markdown_converter.py` | `simple_text()` 改为委托调用 `cleaners`；`fastgpt_simple_text()` 保持不变 |

### 3.2 P1-2：水印文本过滤

**目标**：识别并过滤文档中的水印文本。

**常见水印模式**：

| 模式 | 示例 | 检测策略 |
|------|------|---------|
| 对角线重复短文本 | "CONFIDENTIAL"、"内部文件"、"DRAFT" | 重复行检测 |
| 固定位置重复短文本 | 每页出现的公司名 | 重复行检测 |
| 可配置水印关键词 | 用户自定义 | 关键词列表匹配 |

**实现策略**：

1. **重复短行检测**：检测在文本中出现 ≥2 次的短行（≤30 字符），视为水印候选
2. **关键词列表匹配**：提供内置常见水印关键词 + 用户可扩展列表
3. **PDF span 属性过滤**：检测颜色/透明度（P2 阶段，本次不实现）

**新增文件**：`cleaners/rules/watermark.py`

```python
class FilterWatermarkRule(CleanRule):
    name = "filter_watermark"
    description = "过滤文档中的水印文本（重复短行、关键词匹配）"
    default_enabled = False

    # 内置常见水印关键词
    BUILTIN_WATERMARKS = [
        "CONFIDENTIAL", "DRAFT", "INTERNAL", "SAMPLE",
        "机密", "内部文件", "草稿", "样本", "仅供参考",
        "DO NOT DISTRIBUTE", "WATERMARK",
    ]

    def apply(self, text: str, **kwargs) -> str:
        watermark_keywords = kwargs.get(
            "watermark_keywords", self.BUILTIN_WATERMARKS
        )
        min_repeat_count = kwargs.get("watermark_min_repeat", 2)
        max_line_length = kwargs.get("watermark_max_line_length", 30)

        lines = text.split("\n")
        line_counts = Counter(line.strip() for line in lines if line.strip())
        watermark_lines = {
            line for line, count in line_counts.items()
            if count >= min_repeat_count and len(line) <= max_line_length
        }
        # 也匹配关键词
        keyword_lines = {
            line for line in line_counts
            if any(kw in line for kw in watermark_keywords)
        }
        watermark_lines |= keyword_lines

        result_lines = [line for line in lines if line.strip() not in watermark_lines]
        return "\n".join(result_lines)
```

**API 变更**：`CleanOptions` 新增字段

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `filter_watermark` | `bool` | `false` | 启用水印过滤 |
| `watermark_keywords` | `list[str]` | `[]` | 自定义水印关键词（空则使用内置列表） |
| `watermark_min_repeat` | `int` | `2` | 重复行最少出现次数 |
| `watermark_max_line_length` | `int` | `30` | 水印行最大字符数 |

### 3.3 P1-3：重复段落去重

**目标**：检测并移除因版面分析错误导致的重复文本块。

**实现策略**：

1. **精确去重**：按段落分割后计算 SHA256 哈希，移除完全相同的段落
2. **模糊去重**（可选）：基于编辑距离的相似度检测，相似度阈值可配置

**新增文件**：`cleaners/rules/deduplication.py`

```python
class DeduplicateParagraphsRule(CleanRule):
    name = "deduplicate_paragraphs"
    description = "检测并移除重复段落（精确匹配 + 可选模糊匹配）"
    default_enabled = False

    def apply(self, text: str, **kwargs) -> str:
        enable_fuzzy = kwargs.get("dedup_fuzzy", False)
        fuzzy_threshold = kwargs.get("dedup_fuzzy_threshold", 0.9)

        paragraphs = re.split(r'\n{2,}', text)
        seen_hashes = set()
        unique_paragraphs = []

        for para in paragraphs:
            para_stripped = para.strip()
            if not para_stripped:
                unique_paragraphs.append(para)
                continue

            h = hashlib.sha256(para_stripped.encode()).hexdigest()
            if h in seen_hashes:
                continue

            if enable_fuzzy:
                is_similar = False
                for existing in seen_paragraphs:
                    similarity = _compute_similarity(para_stripped, existing)
                    if similarity >= fuzzy_threshold:
                        is_similar = True
                        break
                if is_similar:
                    continue
                seen_paragraphs.append(para_stripped)

            seen_hashes.add(h)
            unique_paragraphs.append(para)

        return "\n\n".join(unique_paragraphs)
```

**模糊相似度算法**：使用 `difflib.SequenceMatcher` 计算编辑距离相似度，无需引入额外依赖。

**API 变更**：`CleanOptions` 新增字段

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `deduplicate_paragraphs` | `bool` | `false` | 启用段落去重 |
| `dedup_fuzzy` | `bool` | `false` | 启用模糊去重 |
| `dedup_fuzzy_threshold` | `float` | `0.9` | 模糊去重相似度阈值（0.0~1.0） |

### 3.4 P1-4：表格清洗

**目标**：针对 Markdown 表格的清洗，移除空行空列，自动识别表头。

**实现策略**：

1. **检测 Markdown 表格**：使用正则匹配 `|...|` 格式
2. **移除全空行**：所有单元格为空的行
3. **移除全空列**：所有行中该列均为空的列
4. **表头行自动识别**：基于分隔行 `|---|` 模式

**新增文件**：`cleaners/rules/table_clean.py`

```python
class CleanTableRule(CleanRule):
    name = "clean_table"
    description = "清洗 Markdown 表格：移除空行空列、确保表头结构正确"
    default_enabled = False

    def apply(self, text: str, **kwargs) -> str:
        # 检测文本中的 Markdown 表格并逐个清洗
        TABLE_PATTERN = re.compile(
            r'(\|(?:[^\n|]*\|)+\n\|(?:[:\-\s]*\|)+\n(?:\|(?:[^\n|]*\|)*\n)*)',
            re.MULTILINE
        )

        def _clean_table(match):
            table_text = match.group(0)
            lines = [l for l in table_text.strip().split('\n') if l.strip()]
            if len(lines) < 2:
                return table_text

            # 解析表格
            rows = [self._parse_row(line) for line in lines]
            header = rows[0]
            separator = lines[1]
            data_rows = rows[2:]

            # 移除全空行
            data_rows = [r for r in data_rows if any(cell.strip() for cell in r)]

            # 移除全空列
            non_empty_cols = self._find_non_empty_cols(header, data_rows)
            if len(non_empty_cols) < len(header):
                header = [header[i] for i in non_empty_cols]
                data_rows = [[r[i] for i in non_empty_cols] for r in data_rows]
                separator = self._rebuild_separator(len(non_empty_cols))

            # 重建表格
            result = self._format_row(header) + '\n' + separator + '\n'
            for row in data_rows:
                result += self._format_row(row) + '\n'
            return result

        return TABLE_PATTERN.sub(_clean_table, text)
```

**API 变更**：`CleanOptions` 新增字段

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `clean_table` | `bool` | `false` | 启用表格清洗 |

### 3.5 P1-5：敏感信息脱敏增强

**目标**：在现有脱敏规则基础上，增加银行卡号、护照号等更多敏感信息类型的检测。

**新增脱敏规则**：

| 类型 | 正则模式 | 替换为 | 示例 |
|------|---------|--------|------|
| 银行卡号（16-19位） | `(?<!\d)(?:62|4|5|3[4-9])\d{14,17}(?!\d)` | `***BANKCARD***` | `6222021234567890123` → `***BANKCARD***` |
| 护照号 | `(?<![A-Za-z0-9])[EK]\d{8}(?![A-Za-z0-9])` | `***PASSPORT***` | `E12345678` → `***PASSPORT***` |
| 军官证 | `(?<![A-Za-z0-9])军字第\d{6,8}号(?![A-Za-z0-9])` | `***MILITARY***` | `军字第123456号` → `***MILITARY***` |

**修改文件**：`cleaners/rules/sensitive.py`（从 `markdown_converter.py` 迁移并增强）

**匹配顺序**（更新后）：身份证号 → 银行卡号 → 护照号 → 军官证 → 手机号 → 邮箱 → IP 地址

> 银行卡号在手机号之前，因为银行卡号可能包含手机号模式的子串。

**API 变更**：`CleanOptions` 无新增字段，`mask_sensitive` 开关控制所有脱敏规则。

***

## 4. API 变更汇总

### 4.1 POST /api/clean

`CleanOptions` 新增字段：

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `filter_watermark` | `bool` | `false` | 水印文本过滤 |
| `watermark_keywords` | `list[str]` | `[]` | 自定义水印关键词 |
| `watermark_min_repeat` | `int` | `2` | 水印行最少重复次数 |
| `watermark_max_line_length` | `int` | `30` | 水印行最大字符数 |
| `deduplicate_paragraphs` | `bool` | `false` | 段落去重 |
| `dedup_fuzzy` | `bool` | `false` | 模糊去重 |
| `dedup_fuzzy_threshold` | `float` | `0.9` | 模糊去重相似度阈值 |
| `clean_table` | `bool` | `false` | 表格清洗 |

完整 `CleanOptions` 字段列表（P1 完成后）：

```json
{
  "trim": true,
  "normalize_unicode": true,
  "remove_invisible_chars": true,
  "remove_chinese_space": true,
  "normalize_newline": true,
  "fix_hyphenation": true,
  "collapse_whitespace": true,
  "remove_empty_lines": true,
  "filter_watermark": false,
  "watermark_keywords": [],
  "watermark_min_repeat": 2,
  "watermark_max_line_length": 30,
  "deduplicate_paragraphs": false,
  "dedup_fuzzy": false,
  "dedup_fuzzy_threshold": 0.9,
  "clean_table": false,
  "mask_sensitive": false,
  "filter_special_chars": false
}
```

### 4.2 前端 UI 变更

在「数据清洗」步骤的「高级选项」区域新增：

| 控件 | 类型 | 说明 |
|------|------|------|
| 水印文本过滤 | checkbox | 启用/禁用水印过滤 |
| 段落去重 | checkbox | 启用/禁用段落去重 |
| 模糊去重 | checkbox | 仅在段落去重启用时显示 |
| 表格清洗 | checkbox | 启用/禁用表格清洗 |

同时更新 `CLEAN_RULE_DESCRIPTIONS` 常量，为新增规则添加 tooltip 说明。

***

## 5. 实施任务分解

### Task 1：建立 CleanRule 基类和注册机制

**文件**：
- 创建：`cleaners/base.py`
- 创建：`cleaners/registry.py`
- 创建：`cleaners/pipeline.py`
- 创建：`cleaners/rules/__init__.py`

- [ ] Step 1: 创建 `cleaners/base.py`，定义 `CleanRule` 抽象基类
- [ ] Step 2: 创建 `cleaners/registry.py`，实现规则注册表
- [ ] Step 3: 创建 `cleaners/pipeline.py`，实现 `CleanPipeline` 管道执行器
- [ ] Step 4: 创建 `cleaners/rules/__init__.py`，定义规则自动注册机制
- [ ] Step 5: 编写单元测试验证基类和注册机制

### Task 2：迁移现有清洗逻辑为规则化

**文件**：
- 创建：`cleaners/rules/whitespace.py`
- 创建：`cleaners/rules/unicode.py`
- 创建：`cleaners/rules/chinese_text.py`
- 创建：`cleaners/rules/hyphenation.py`
- 创建：`cleaners/rules/sensitive.py`
- 创建：`cleaners/rules/special_chars.py`
- 修改：`cleaners/text_cleaner.py`
- 修改：`cleaners/__init__.py`

- [ ] Step 1: 创建 whitespace.py，实现 TrimRule, CollapseWhitespaceRule, RemoveEmptyLinesRule, NormalizeNewlineRule
- [ ] Step 2: 创建 unicode.py，实现 NormalizeUnicodeRule, RemoveInvisibleCharsRule
- [ ] Step 3: 创建 chinese_text.py，实现 RemoveChineseSpaceRule
- [ ] Step 4: 创建 hyphenation.py，实现 FixHyphenationRule
- [ ] Step 5: 创建 sensitive.py，实现 MaskSensitiveRule（含增强的银行卡号、护照号、军官证）
- [ ] Step 6: 创建 special_chars.py，实现 FilterSpecialCharsRule
- [ ] Step 7: 修改 text_cleaner.py，simple_text() 改为委托 CleanPipeline
- [ ] Step 8: 修改 __init__.py，更新导出
- [ ] Step 9: 运行回归测试，确保现有清洗行为不变

### Task 3：实现水印文本过滤规则

**文件**：
- 创建：`cleaners/rules/watermark.py`
- 修改：`app.py`（CleanOptions 新增字段）
- 修改：`cleaners/rules/__init__.py`（注册新规则）

- [ ] Step 1: 编写水印过滤的失败测试
- [ ] Step 2: 实现 FilterWatermarkRule
- [ ] Step 3: 更新 app.py 的 CleanOptions
- [ ] Step 4: 运行测试验证

### Task 4：实现重复段落去重规则

**文件**：
- 创建：`cleaners/rules/deduplication.py`
- 修改：`app.py`（CleanOptions 新增字段）
- 修改：`cleaners/rules/__init__.py`（注册新规则）

- [ ] Step 1: 编写段落去重的失败测试
- [ ] Step 2: 实现 DeduplicateParagraphsRule（精确去重 + 模糊去重）
- [ ] Step 3: 更新 app.py 的 CleanOptions
- [ ] Step 4: 运行测试验证

### Task 5：实现表格清洗规则

**文件**：
- 创建：`cleaners/rules/table_clean.py`
- 修改：`app.py`（CleanOptions 新增字段）
- 修改：`cleaners/rules/__init__.py`（注册新规则）

- [ ] Step 1: 编写表格清洗的失败测试
- [ ] Step 2: 实现 CleanTableRule
- [ ] Step 3: 更新 app.py 的 CleanOptions
- [ ] Step 4: 运行测试验证

### Task 6：敏感信息脱敏增强

**文件**：
- 修改：`cleaners/rules/sensitive.py`（新增银行卡号、护照号、军官证规则）

- [ ] Step 1: 编写新增脱敏规则的失败测试
- [ ] Step 2: 在 MaskSensitiveRule 中新增银行卡号、护照号、军官证正则
- [ ] Step 3: 运行测试验证

### Task 7：更新前端 UI

**文件**：
- 修改：`KnowledgeProcessDemo.vue`

- [ ] Step 1: 更新 cleanOptions 响应式变量，新增 P1 字段
- [ ] Step 2: 更新 CLEAN_RULE_DESCRIPTIONS，新增 P1 规则说明
- [ ] Step 3: 在高级选项区域新增水印过滤、段落去重、表格清洗控件
- [ ] Step 4: 构建前端验证

### Task 8：集成测试和回归验证

- [ ] Step 1: 运行完整测试套件 `pytest tests/ -v`
- [ ] Step 2: 手动测试前端 Demo 全流程
- [ ] Step 3: 验证向后兼容性（现有 API 调用不受影响）

***

## 6. 修改文件清单

| 文件路径 | 变更类型 | 变更摘要 |
|---------|---------|---------|
| `cleaners/base.py` | 新增 | CleanRule 抽象基类 |
| `cleaners/registry.py` | 新增 | 规则注册表 |
| `cleaners/pipeline.py` | 新增 | CleanPipeline 管道执行器 |
| `cleaners/rules/__init__.py` | 新增 | 规则模块导出 + 自动注册 |
| `cleaners/rules/whitespace.py` | 新增 | 空白/换行规则（4 个 Rule） |
| `cleaners/rules/unicode.py` | 新增 | Unicode 规则（2 个 Rule） |
| `cleaners/rules/chinese_text.py` | 新增 | 中文文本规则（1 个 Rule） |
| `cleaners/rules/hyphenation.py` | 新增 | 连字符断行修复规则 |
| `cleaners/rules/sensitive.py` | 新增 | 敏感信息脱敏规则（含增强） |
| `cleaners/rules/special_chars.py` | 新增 | 特殊字符过滤规则 |
| `cleaners/rules/watermark.py` | 新增 | 水印文本过滤规则 |
| `cleaners/rules/deduplication.py` | 新增 | 重复段落去重规则 |
| `cleaners/rules/table_clean.py` | 新增 | 表格清洗规则 |
| `cleaners/text_cleaner.py` | 修改 | simple_text() 委托 CleanPipeline |
| `cleaners/__init__.py` | 修改 | 更新导出 |
| `converters/markdown_converter.py` | 修改 | simple_text() 委托 cleaners |
| `app.py` | 修改 | CleanOptions 新增 P1 字段 |
| `KnowledgeProcessDemo.vue` | 修改 | 新增 P1 清洗选项 UI |

***

## 7. 风险评估

| 风险项 | 等级 | 说明 | 缓解措施 |
|--------|------|------|---------|
| 规则化重构引入回归 | 🟠 中 | 迁移现有逻辑可能改变行为 | 严格回归测试，确保现有测试全部通过 |
| 水印过滤误删正文 | 🟡 中 | 重复短行可能包含合法内容 | 默认关闭，提供关键词白名单 |
| 段落去重误删 | 🟡 中 | 合法重复段落被误删 | 默认关闭，模糊去重阈值可调 |
| 表格清洗破坏格式 | 🟡 中 | 空列移除可能改变表格语义 | 默认关闭，仅移除全空行/列 |
| 银行卡号误匹配 | 🟡 中 | 长数字串可能非银行卡 | 使用严格正则 + 边界断言 |
| 模糊去重性能 | 🟢 低 | O(n²) 相似度计算 | 仅在启用模糊去重时执行，大文档可关闭 |

***

## 8. 向后兼容性

| 验证项 | 预期结果 |
|--------|---------|
| `simple_text("  hello  world  \n\n\n  ")` | 与 P0 行为一致 |
| `fastgpt_simple_text(...)` | 行为不变（未使用 pipeline） |
| `simple_markdown_text(...)` | 行为不变（未使用 pipeline） |
| `/api/clean` 端点默认参数 | 输出与 P0 一致 |
| 所有 P1 新增字段默认关闭 | 不影响现有行为 |
