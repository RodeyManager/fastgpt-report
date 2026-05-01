# 数据清洗功能扩展分析文档

> **项目**: fastgpt-report / knowledge-process-api
> **日期**: 2026-04-30
> **目标**: 基于 RAGflow 数据清洗规则，分析当前项目扩展数据清洗功能的优先路径

***

## 1. 当前项目数据清洗能力现状

### 1.1 架构概览

当前项目的文档处理流水线为五步结构：

```
文件上传 → 解析(Parse) → 转换(Convert) → 清洗(Clean) → 分块(Chunk) → 图片索引(Index)
```

数据清洗模块位于 `knowledge-process-api/src/fastgpt_demo/` 下，核心代码分布：

| 模块         | 文件                                 | 职责                         |
| ---------- | ---------------------------------- | -------------------------- |
| Cleaners   | `cleaners/text_cleaner.py`         | 清洗入口（重新导出 converters 中的函数） |
| Converters | `converters/markdown_converter.py` | **清洗核心逻辑所在**，包含 3 个清洗函数    |
| Parsers    | `parsers/pdf_parser.py`            | PDF 解析时内置页眉页脚过滤（5% 阈值）     |
| Chunkers   | `chunkers/text_chunker.py`         | 分块后轻量规范化（`_simple_text`）   |

### 1.2 当前清洗规则清单

<br />

当前清洗功能由 `simple_text()` 函数实现，提供 **5 个独立开关**：

| 规则        | 开关名                    | 实现                                                           | 默认 |
| --------- | ---------------------- | ------------------------------------------------------------ | -- |
| 去首尾空白     | `trim`                 | `text.strip()`                                               | ✅  |
| 移除中文字符间空格 | `remove_chinese_space` | `re.sub(r"([\u4e00-\u9fa5])[^\S\n]+([\u4e00-\u9fa5])", ...)` | ✅  |
| 规范化换行符    | `normalize_newline`    | `\r\n` / `\r` → `\n`                                         | ✅  |
| 合并连续空白    | `collapse_whitespace`  | 2+ 连续非换行空白 → 1 空格                                            | ✅  |
| 移除空行      | `remove_empty_lines`   | 3+ 连续换行 → 2 换行                                               | ✅  |
| 控制字符替换    | *(始终执行)*               | `\x00-\x08` → 空格                                             | ✅  |

另外，`fastgpt_simple_text()` 是上述 5 个开关全开的固定版本，`simple_markdown_text()` 在 `fastgpt_simple_text()` 基础上增加 Markdown 后处理（链接清理、反斜杠转义移除、`\\n` 还原、结构元素前空格清理）。

### 1.3 当前清洗的局限性

1. **纯文本级清洗**：只处理字符和空白，不理解文档结构
2. **无文档类型感知**：所有文档类型使用同一套清洗规则
3. **无结构级清洗**：不支持页眉页脚识别（仅 PDF 硬编码 5%）、水印过滤、目录过滤、脚注处理
4. **无表格感知清洗**：不处理合并单元格、空行空列、表头识别
5. **无重复检测**：不检测重复段落
6. **无语义增强**：不支持摘要生成、关键词提取、问题生成等 Transformer 级处理
7. **清洗与解析耦合不足**：PDF 解析器的页眉页脚过滤是硬编码阈值，不可配置

***

## 2. RAGflow 数据清洗规则分析

### 2.1 RAGflow 架构：可编排的 Ingestion Pipeline

RAGflow v0.21+ 引入了 **Ingestion Pipeline** 架构，将数据处理拆分为三个阶段：

```
Parser（解析） → Transformer（转换/增强） → Indexer（索引）
```

核心设计理念：**先理解、后处理** — 通过深度文档理解模型识别文档结构，再基于结构信息进行精准的清洗和分块。

### 2.2 RAGflow 清洗规则体系

#### 2.2.1 文本级清洗

| 规则      | 说明                                          |     当前项目是否支持     |
| ------- | ------------------------------------------- | :--------------: |
| 页眉页脚过滤  | 基于版面分析结果，过滤标记为 header/footer 的区域            |  ⚠️ 仅 PDF 硬编码 5% |
| 控制字符移除  | 移除 `\x00-\x08`, `\x0b`, `\x0c`, `\x0e-\x1f` | ⚠️ 仅 `\x00-\x08` |
| 空白规范化   | 合并连续空格、规范化换行符                               |         ✅        |
| 空行处理    | 3+ 连续换行压缩为 2                                |         ✅        |
| 特殊符号清理  | PDF 乱码字符清理、连字符断行修复                          |         ❌        |
| 中文字符间空格 | 移除中文字符间多余空格                                 |         ✅        |

#### 2.2.2 结构级清洗

| 规则      | 说明                   | 当前项目是否支持 |
| ------- | -------------------- | :------: |
| 重复段落去重  | 检测并移除因版面分析错误导致的重复文本块 |     ❌    |
| 水印文本过滤  | 识别并过滤常见水印文本模式        |     ❌    |
| 目录区域过滤  | 可选过滤自动生成的目录区域        |     ❌    |
| 脚注/尾注处理 | 可选保留或过滤脚注内容          |     ❌    |
| 页码过滤    | 移除页码文本               |     ❌    |

#### 2.2.3 表格清洗

| 规则      | 说明             | 当前项目是否支持 |
| ------- | -------------- | :------: |
| 合并单元格还原 | 将合并单元格展开为完整结构  |     ❌    |
| 空行/空列移除 | 移除表格中的空行和空列    |     ❌    |
| 表头识别    | 自动识别表头行，确保结构正确 |     ❌    |

#### 2.2.4 文档类型专用解析（RAGflow 独有）

| 解析方法           | 说明                 | 当前项目是否支持 |
| -------------- | ------------------ | :------: |
| `general`      | 通用解析               |  ⚠️ 部分支持 |
| `naive`        | 简单解析，按固定 token 数切分 |     ❌    |
| `table`        | 表格专用解析             |     ❌    |
| `paper`        | 论文专用解析             |     ❌    |
| `book`         | 书籍专用解析             |     ❌    |
| `laws`         | 法律文书专用解析           |     ❌    |
| `presentation` | 演示文稿解析             |     ❌    |
| `qa`           | Q\&A 格式解析          |     ❌    |
| `resume`       | 简历解析               |     ❌    |
| `one`          | 整篇文档作为一个块          |     ❌    |

#### 2.2.5 Transformer 语义增强（RAGflow 独有）

| 功能    | 说明            | 当前项目是否支持 |
| ----- | ------------- | :------: |
| 摘要生成  | 为文档/分块生成摘要    |     ❌    |
| 关键词提取 | 提取文档关键词       |     ❌    |
| 问题生成  | 生成潜在问题以提升检索匹配 |     ❌    |
| 元数据生成 | 生成结构化元数据      |     ❌    |

### 2.3 RAGflow 分块策略对比

| 维度    | RAGflow                | 当前项目                 |
| ----- | ---------------------- | -------------------- |
| 分块基础  | Token 计数（tiktoken）     | 字符计数                 |
| 分块策略  | 按标题 / 按 Token / 自定义分隔符 | 递归多策略优先级链（12+ 规则）    |
| 专用模板  | 10+ 种文档类型专用模板          | 无                    |
| 重叠机制  | 可配置百分比                 | 可配置比例（默认 15%）        |
| 分块后处理 | 过短块合并、过长块再切分、元数据附加     | `_simple_text` 轻量规范化 |

***

## 3. 差距分析与扩展优先级

### 3.1 核心差距矩阵

将 RAGflow 的清洗能力按 **实现难度** 和 **业务价值** 两个维度评估：

| 扩展项                   | 实现难度 |  业务价值 | 优先级 |
| --------------------- | :--: | :---: | :-: |
| 扩展控制字符范围（`\x00-\x1f`） | 🟢 低 |  🟡 中 |  P0 |
| PDF 页眉页脚过滤可配置化        | 🟢 低 |  🟡 中 |  P0 |
| 连字符断行修复               | 🟢 低 |  🟡 中 |  P0 |
| 水印文本过滤                | 🟢 低 |  🟠 高 |  P1 |
| 重复段落去重                | 🟡 中 |  🟠 高 |  P1 |
| 目录区域过滤                | 🟡 中 |  🟡 中 |  P1 |
| 脚注/尾注处理               | 🟡 中 |  🟡 中 |  P2 |
| 表格清洗（空行空列、表头识别）       | 🟡 中 |  🟠 高 |  P1 |
| 文档类型专用清洗策略            | 🔴 高 |  🟠 高 |  P2 |
| Transformer 语义增强      | 🔴 高 | 🔴 极高 |  P3 |
| 版面分析模型集成              | 🔴 高 |  🟠 高 |  P3 |

### 3.2 优先级说明

- **P0（立即执行）**：改动小、风险低、可立即提升清洗质量
- **P1（短期目标）**：中等难度、高业务价值，需要一定设计工作
- **P2（中期目标）**：需要较多设计工作和代码重构
- **P3（长期目标）**：依赖外部模型或大规模架构调整

***

## 4. 扩展方案：首先该做什么

### 4.1 第一步：完善清洗规则引擎（P0）

**目标**：在不改变现有架构的前提下，补齐基础清洗规则。

#### 4.1.1 扩展控制字符范围

当前仅替换 `\x00-\x08`，RAGflow 覆盖 `\x00-\x1f`（含 `\x0b`, `\x0c`, `\x0e-\x1f`）。

**影响范围**：

- `converters/markdown_converter.py` 中的 `fastgpt_simple_text()`、`simple_text()`
- `chunkers/text_chunker.py` 中的 `_simple_text()`

**改动点**：将 `re.sub(r"[\x00-\x08]", " ", text)` 扩展为 `re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", text)`

> 注意：保留 `\x09`(Tab)、`\x0a`(LF)、`\x0d`(CR) 不替换，它们是有意义的空白字符。

#### 4.1.2 PDF 页眉页脚过滤可配置化

当前 `pdf_parser.py` 中硬编码 `0.05`（5%）阈值，应改为可配置参数。

**影响范围**：

- `parsers/pdf_parser.py` 的 `_extract_page_text()` 函数
- `parsers/__init__.py` 的 `parse_file()` 函数签名
- `app.py` 的 `/api/parse` 端点

**改动点**：

1. 为 `parse_file()` 和 `parse_pdf()` 增加 `header_footer_ratio` 参数（默认 `0.05`）
2. 在 `ParseRequest` 中增加可选参数
3. 前端 Demo 增加配置入口

#### 4.1.3 连字符断行修复

PDF 提取中常见的英文断行问题，如 `com-\nputer` 应修复为 `computer`。

**影响范围**：

- `converters/markdown_converter.py` 的 `simple_text()` 函数

**改动点**：增加可选规则 `fix_hyphenation`，正则 `re.sub(r"(\w)-\n(\w)", r"\1\2", text)`

### 4.2 第二步：增加结构级清洗规则（P1）

**目标**：引入文档结构感知的清洗能力。

#### 4.2.1 水印文本过滤

常见水印模式包括：

- 对角线重复文本（如 "CONFIDENTIAL"、"内部文件"）
- 固定位置重复出现的短文本
- 半透明或灰色文本（PDF 中可检测）

**实现策略**：

1. 基于正则的模式匹配（检测重复出现的短文本行）
2. 基于 PDF span 属性的过滤（检测颜色、透明度）
3. 可配置水印文本列表

#### 4.2.2 重复段落去重

检测连续或非连续的重复文本块。

**实现策略**：

1. 按段落分割后计算哈希
2. 检测完全相同的段落
3. 可选：基于编辑距离的模糊去重（相似度阈值可配置）

#### 4.2.3 表格清洗

针对 Markdown 表格和 CSV/XLSX 解析结果的清洗。

**实现策略**：

1. 移除全空行（所有单元格为空）
2. 移除全空列
3. 表头行自动识别（基于分隔行 `|---|` 模式）

### 4.3 第三步：文档类型感知清洗（P2）

**目标**：根据文档类型应用不同的清洗策略。

**设计方向**：

1. 扩展 `CleanOptions` 为 `CleanProfile`，按文档类型预设不同的清洗配置
2. 定义清洗配置文件（Clean Profile），如 `pdf_academic`、`pdf_business`、`docx_report` 等
3. 每个配置文件定义启用哪些清洗规则及其参数

### 4.4 第四步：语义增强（P3）

**目标**：引入 LLM 驱动的语义增强能力。

**设计方向**：

1. 新增 `Transformer` 模块，支持摘要生成、关键词提取、问题生成
2. 支持三种模式：Improvise / Precise / Balance
3. 可配置 LLM 后端（OpenAI / 本地模型等）

***

## 5. 架构扩展建议

### 5.1 当前架构问题

1. **清洗逻辑分散**：核心清洗逻辑在 `converters/markdown_converter.py` 而非 `cleaners/` 模块
2. **Cleaners 模块空壳**：`cleaners/text_cleaner.py` 仅重新导出 converters 的函数
3. **清洗与转换耦合**：`simple_markdown_text()` 同时处理 Markdown 后处理和文本清洗
4. **无清洗规则注册机制**：新增清洗规则需要修改核心函数

### 5.2 建议的架构调整方向

```
cleaners/
├── __init__.py              # 模块导出
├── registry.py              # 清洗规则注册表
├── base.py                  # CleanRule 基类 / CleanProfile 定义
├── rules/
│   ├── __init__.py
│   ├── whitespace.py        # 空白/换行相关规则
│   ├── control_chars.py     # 控制字符规则
│   ├── chinese_text.py      # 中文文本规则
│   ├── hyphenation.py       # 连字符断行修复
│   ├── watermark.py         # 水印过滤
│   ├── deduplication.py     # 重复段落去重
│   ├── table_clean.py       # 表格清洗
│   └── markdown_post.py     # Markdown 后处理
├── profiles/
│   ├── __init__.py
│   ├── default.py           # 默认清洗配置
│   ├── pdf_academic.py      # 学术 PDF 配置
│   └── pdf_business.py      # 商务 PDF 配置
└── pipeline.py              # 清洗管道（按配置执行规则链）
```

**核心设计原则**：

1. **规则即插件**：每条清洗规则是独立的 `CleanRule` 实例，可独立启用/禁用
2. **配置驱动**：通过 `CleanProfile` 定义规则组合和参数
3. **管道执行**：`CleanPipeline` 按 Profile 配置顺序执行规则链
4. **向后兼容**：保留 `clean_text()` / `simple_text()` 等现有 API 不变

### 5.3 API 扩展方向

当前 `/api/clean` 端点的 `CleanOptions` 仅 5 个布尔开关。扩展后应支持：

```python
class CleanRuleConfig(BaseModel):
    enabled: bool = True
    params: dict = {}

class CleanProfileRequest(BaseModel):
    text: str
    profile: str = "default"           # 预设配置名
    rules: dict[str, CleanRuleConfig]  # 规则级覆盖
    # 向后兼容：保留原有 5 个开关
    options: CleanOptions = Field(default_factory=CleanOptions)
```

***

## 6. 实施路线图

### Phase 1：基础补齐（P0，预计 1-2 天）

| 任务             | 改动文件                                       | 风险 |
| -------------- | ------------------------------------------ | -- |
| 扩展控制字符范围       | `markdown_converter.py`, `text_chunker.py` | 低  |
| PDF 页眉页脚过滤可配置化 | `pdf_parser.py`, `__init__.py`, `app.py`   | 低  |
| 连字符断行修复        | `markdown_converter.py`                    | 低  |
| 补充测试用例         | `tests/`                                   | 低  |

### Phase 2：结构级清洗（P1，预计 3-5 天）

| 任务                   | 改动文件                              | 风险 |
| -------------------- | --------------------------------- | -- |
| 设计 CleanRule 基类和注册机制 | `cleaners/` 新文件                   | 中  |
| 实现水印文本过滤规则           | `cleaners/rules/watermark.py`     | 中  |
| 实现重复段落去重规则           | `cleaners/rules/deduplication.py` | 中  |
| 实现表格清洗规则             | `cleaners/rules/table_clean.py`   | 中  |
| 重构现有清洗逻辑为规则化         | `cleaners/`, `converters/`        | 中  |
| 更新 API 和前端           | `app.py`, Demo 前端                 | 中  |

### Phase 3：文档类型感知（P2，预计 5-7 天）

| 任务                 | 改动文件                           | 风险 |
| ------------------ | ------------------------------ | -- |
| 设计 CleanProfile 机制 | `cleaners/profiles/`           | 中  |
| 实现预设配置文件           | `cleaners/profiles/`           | 低  |
| 目录区域过滤规则           | `cleaners/rules/toc_filter.py` | 中  |
| 脚注/尾注处理规则          | `cleaners/rules/footnote.py`   | 中  |
| 更新 API 和前端         | `app.py`, Demo 前端              | 中  |

### Phase 4：语义增强（P3，预计 7-14 天）

| 任务                  | 改动文件                          | 风险 |
| ------------------- | ----------------------------- | -- |
| 设计 Transformer 模块架构 | `transformers/` 新模块           | 高  |
| 集成 LLM 后端           | `transformers/llm_backend.py` | 高  |
| 实现摘要生成              | `transformers/summary.py`     | 中  |
| 实现关键词提取             | `transformers/keywords.py`    | 中  |
| 实现问题生成              | `transformers/questions.py`   | 中  |
| 更新 API 和前端          | `app.py`, Demo 前端             | 中  |

***

## 7. 关键注意事项

### 7.1 向后兼容性

- **API 兼容**：`/api/clean` 端点的现有 `CleanOptions` 必须继续工作
- **函数签名兼容**：`clean_text()` / `simple_text()` / `fastgpt_simple_text()` 的现有调用方式不变
- **分块兼容**：`_simple_text()` 在 `text_chunker.py` 中的行为应与 `fastgpt_simple_text()` 保持一致

### 7.2 性能考量

- 水印过滤和重复去重可能涉及全文扫描，需注意大文件性能
- 正则规则链应按短路原则排列（高命中率规则优先）
- 表格清洗应仅在检测到表格时执行

### 7.3 测试策略

- 每条新清洗规则必须有独立的单元测试
- 回归测试确保现有清洗行为不变
- 集成测试覆盖完整流水线（解析 → 清洗 → 分块）

***

## 附录 A：当前项目清洗代码关键位置

| 文件                                 | 行号       | 内容                                       |
| ---------------------------------- | -------- | ---------------------------------------- |
| `converters/markdown_converter.py` | L55-82   | `fastgpt_simple_text()` — 基础清洗           |
| `converters/markdown_converter.py` | L89-130  | `simple_markdown_text()` — Markdown 后处理  |
| `converters/markdown_converter.py` | L146-175 | `simple_text()` — 交互式清洗（5 开关）            |
| `cleaners/text_cleaner.py`         | L1-14    | 清洗模块入口（重新导出）                             |
| `chunkers/text_chunker.py`         | L42-54   | `_simple_text()` — 分块后规范化                |
| `parsers/pdf_parser.py`            | L15-59   | `_extract_page_text()` — PDF 页眉页脚过滤      |
| `app.py`                           | L94-108  | `CleanOptions` / `CleanRequest` — API 模型 |

## 附录 B：RAGflow 参考资源

| 资源                            | 链接                                                                                                                                |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| RAGflow GitHub                | <https://github.com/infiniflow/ragflow>                                                                                           |
| RAGflow Ingestion Pipeline 博文 | <https://www.ragflow.io/blog/is-data-processing-like-building-with-lego-here-is-a-detailed-explanation-of-the-ingestion-pipeline> |
| RAGflow v0.21.0 发布说明          | <https://ragflow.io/blog/ragflow-0.21.0-ingestion-pipeline-long-context-rag-and-admin-cli>                                        |
| RAGflow 分块方法源码                | <https://github.com/infiniflow/ragflow/tree/main/rag/app>                                                                         |

