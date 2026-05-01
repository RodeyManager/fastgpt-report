# 数据清洗规则实施计划 — 对比 RAGflow 全景规划

> **项目**: fastgpt-report / knowledge-process-api
> **日期**: 2026-05-01
> **目标**: 对比 GitHub RAGflow 项目，规划本项目数据清洗规则的完整实施路线图

***

## 1. 项目现状总结

### 1.1 已完成工作（P0 + P1）

本项目已完成 P0（基础清洗规则补齐）和 P1（结构级清洗规则 + CleanRule 架构）两个阶段，当前清洗能力如下：

#### 架构层面

| 组件           | 文件                         | 状态                 |
| ------------ | -------------------------- | ------------------ |
| CleanRule 基类 | `cleaners/base.py`         | ✅ 已实现              |
| 规则注册表        | `cleaners/registry.py`     | ✅ 已实现              |
| 清洗管道         | `cleaners/pipeline.py`     | ✅ 已实现              |
| 清洗入口         | `cleaners/text_cleaner.py` | ✅ 已实现（委托 pipeline） |
| API 模型       | `app.py` CleanOptions      | ✅ 已实现（18 个字段）      |
| 前端 UI        | `KnowledgeProcessDemo.vue` | ✅ 已实现（含 tooltip）   |

#### 清洗规则清单（13 条）

| 规则               | name                     | 默认启用 | 来源阶段 |
| ---------------- | ------------------------ | ---- | ---- |
| 去首尾空白            | `trim`                   | ✅    | P0   |
| Unicode NFKC 标准化 | `normalize_unicode`      | ✅    | P0   |
| 移除不可见字符          | `remove_invisible_chars` | ✅    | P0   |
| 移除中文字符间空格        | `remove_chinese_space`   | ✅    | P0   |
| 规范化换行符           | `normalize_newline`      | ✅    | P0   |
| 连字符断行修复          | `fix_hyphenation`        | ✅    | P0   |
| 合并连续空白           | `collapse_whitespace`    | ✅    | P0   |
| 移除空行             | `remove_empty_lines`     | ✅    | P0   |
| 水印文本过滤           | `filter_watermark`       | ❌    | P1   |
| 重复段落去重           | `deduplicate_paragraphs` | ❌    | P1   |
| 表格清洗             | `clean_table`            | ❌    | P1   |
| 敏感信息脱敏           | `mask_sensitive`         | ❌    | P0   |
| 特殊字符过滤           | `filter_special_chars`   | ❌    | P0   |

#### 规则执行顺序

```
trim → normalize_unicode → remove_invisible_chars → remove_chinese_space
→ normalize_newline → fix_hyphenation → collapse_whitespace → remove_empty_lines
→ filter_watermark → deduplicate_paragraphs → clean_table
→ mask_sensitive → filter_special_chars → 控制字符替换（始终执行）
```

### 1.2 当前架构优势

1. **规则即插件**：每条规则是独立的 `CleanRule` 实例，可独立启用/禁用
2. **配置驱动**：通过 `CleanOptions` 控制规则组合和参数
3. **管道执行**：`CleanPipeline` 按注册顺序执行规则链
4. **向后兼容**：保留 `clean_text()` / `simple_text()` 等现有 API 不变

### 1.3 当前架构不足

1. **无文档类型感知**：所有文档类型使用同一套清洗规则，无法根据 PDF/DOCX/CSV 等类型自动选择最佳策略
2. **无清洗配置预设**：缺少 CleanProfile 机制，用户每次需手动配置所有规则
3. **缺少结构级规则**：无目录过滤、脚注处理、页码过滤等规则
4. **清洗与转换耦合**：`markdown_converter.py` 中仍保留 `simple_text()` 的完整实现，与 `cleaners/` 模块存在逻辑重复
5. **分块策略单一**：仅支持递归多策略分块，无文档类型专用分块策略
6. **无语义增强**：不支持 LLM 驱动的摘要生成、关键词提取等

***

## 2. RAGflow 对比分析

### 2.1 RAGflow Ingestion Pipeline 架构

RAGflow v0.21+ 的数据处理管道为三阶段结构：

```
Parser（解析 + 版面分析） → Transformer（清洗 + 语义增强 + 分块） → Indexer（索引）
```

核心设计理念：**先理解、后处理** — 通过 DeepDoc 版面分析模型识别文档结构，再基于结构信息进行精准清洗和分块。

### 2.2 能力差距矩阵

| 能力维度                | RAGflow                     | 本项目                | 差距   |
| ------------------- | --------------------------- | ------------------ | ---- |
| **文本级清洗**           | 控制字符、空白、换行、连字符、中文空格         | ✅ 全部实现             | 无    |
| **Unicode 标准化**     | NFKC                        | ✅ 已实现              | 无    |
| **不可见字符移除**         | 零宽空格、BOM 等                  | ✅ 已实现              | 无    |
| **水印过滤**            | 重复短行 + 关键词                  | ✅ 已实现              | 无    |
| **段落去重**            | 精确 + 模糊                     | ✅ 已实现              | 无    |
| **表格清洗**            | 空行空列、表头识别                   | ✅ 已实现              | 无    |
| **敏感信息脱敏**          | 身份证/手机/邮箱/IP                | ✅ 已实现（含银行卡/护照/军官证） | 无    |
| **特殊字符过滤**          | 白名单模式                       | ✅ 已实现              | 无    |
| **HTML 干扰标签移除**      | 8 种标签 decompose             | ⚠️ 仅 4 种（markdownify strip） | 🟡 中 |
| **HTML 内容区域识别**      | 5 级优先级策略                   | ❌ 未实现              | 🟡 中 |
| **HTML 实体转换**         | 18 种命名实体 + 数字引用           | ⚠️ 依赖 markdownify 内部处理   | 🟡 中 |
| **HTML 注释移除**         | 支持                          | ❌ 未实现              | 🟢 低 |
| **HTML 噪声模式过滤**      | 版权/备案/广告等 10 种正则         | ❌ 未实现              | 🟡 中 |
| **页眉页脚过滤**          | DeepDoc 版面分析                | ⚠️ 仅 PDF 比例裁剪      | 🟡 中 |
| **目录区域过滤**          | DeepDoc 结构识别                | ❌ 未实现              | 🟠 高 |
| **脚注/尾注处理**         | DeepDoc 结构识别                | ❌ 未实现              | 🟡 中 |
| **页码过滤**            | DeepDoc 结构识别                | ❌ 未实现              | 🟡 中 |
| **文档类型感知清洗**        | 10+ 种专用解析器                  | ❌ 未实现              | 🔴 高 |
| **CleanProfile 预设** | 按 chunk\_method 自动配置        | ❌ 未实现              | 🟠 高 |
| **专用分块策略**          | paper/book/laws/qa/resume 等 | ❌ 仅通用递归分块          | 🔴 高 |
| **语义增强**            | LLM 摘要/关键词/问题生成             | ❌ 未实现              | 🔴 高 |
| **版面分析模型**          | DeepDoc 视觉模型                | ❌ 未实现              | 🔴 高 |

### 2.3 差距优先级评估

| 扩展项               | 实现难度 |  业务价值 | 优先级 |
| ----------------- | :--: | :---: | :-: |
| Markdown 后处理规则化   | 🟢 低 |  🟡 中 |  P2 |
| 目录区域过滤            | 🟢 低 |  🟡 中 |  P2 |
| 页码过滤              | 🟢 低 |  🟡 中 |  P2 |
| 脚注/尾注处理           | 🟡 中 |  🟡 中 |  P2 |
| HTML 干扰标签移除+内容区域识别 | 🟡 中 |  🟠 高 |  P2 |
| HTML 实体转换+注释移除   | 🟢 低 |  🟡 中 |  P2 |
| HTML 噪声模式过滤       | 🟢 低 |  🟡 中 |  P2 |
| CleanProfile 预设机制 | 🟡 中 |  🟠 高 |  P2 |
| 清洗与转换解耦           | 🟡 中 |  🟠 高 |  P2 |
| 文档类型感知清洗          | 🟡 中 |  🟠 高 |  P2 |
| 专用分块策略            | 🔴 高 |  🟠 高 |  P3 |
| 语义增强（LLM）         | 🔴 高 | 🔴 极高 |  P3 |
| 版面分析模型集成          | 🔴 高 |  🟠 高 |  P4 |

***

## 3. P2 实施计划：文档类型感知清洗

### 3.1 P2 目标

1. 建立 CleanProfile 预设机制，按文档类型自动选择清洗规则组合
2. 补齐结构级清洗规则（目录过滤、页码过滤、脚注处理）
3. 新增 HTML 内容过滤能力（干扰标签移除、内容区域识别、实体转换、注释移除、噪声模式过滤）
4. 将 Markdown 后处理规则化，解耦 `markdown_converter.py` 与清洗逻辑
5. 实现文档类型感知的清洗策略自动选择

### 3.2 P2 任务分解（9 个任务）

#### Task 1：Markdown 后处理规则化

**目标**：将 `simple_markdown_text()` 中的后处理逻辑拆分为独立的 CleanRule。

**当前问题**：`simple_markdown_text()` 在 `markdown_converter.py` 中同时处理 Markdown 后处理和文本清洗，与 `cleaners/` 模块逻辑重复。

**新增规则**：

| 规则                 | name                   | 说明             | 默认启用 |
| ------------------ | ---------------------- | -------------- | ---- |
| Markdown 链接清理      | `clean_markdown_links` | 移除链接文本中的换行     | ✅    |
| Markdown 反斜杠转义移除   | `remove_md_escapes`    | 移除不必要的反斜杠转义    | ✅    |
| Markdown 结构元素前空格清理 | `clean_md_structure`   | 移除标题/代码块前的多余空格 | ✅    |

**新增文件**：`cleaners/rules/markdown_post.py`

**修改文件**：

- `cleaners/rules/__init__.py` — 注册新规则
- `cleaners/text_cleaner.py` — 更新导出
- `app.py` — CleanOptions 新增字段

**向后兼容**：`simple_markdown_text()` 保留为快捷方式，内部委托给 pipeline。

***

#### Task 2：目录区域过滤

**目标**：识别并过滤文档中的目录区域。

**实现策略**：

1. 基于正则模式匹配常见目录格式（如 `1.1 xxx .... 12`、`第x节 xxx`）
2. 检测连续的目录条目行（≥3 行）
3. 可配置是否保留目录

**新增规则**：

| 规则     | name         | 说明             | 默认启用 |
| ------ | ------------ | -------------- | ---- |
| 目录区域过滤 | `filter_toc` | 检测并移除自动生成的目录区域 | ❌    |

**新增文件**：`cleaners/rules/toc_filter.py`

**目录检测正则模式**：

```python
# 模式1: 数字编号 + 标题 + 页码
r"^\d+(\.\d+)*\s+.+\s*\.{2,}\s*\d+$"
# 模式2: 第X章/节 + 标题
r"^第[一二三四五六七八九十\d]+[章节]\s+.+$"
# 模式3: 附录/附件
r"^[附录附件]\s*[A-Z\d]*\s+.+$"
```

**API 变更**：CleanOptions 新增 `filter_toc: bool = False`

***

#### Task 3：页码过滤

**目标**：移除文档中独立成行的页码文本。

**实现策略**：

1. 检测独立成行的纯数字（1-4 位）
2. 检测常见页码格式（如 `- 12 -`、`第 12 页`、`Page 12`）
3. 仅在行内无其他文字时过滤

**新增规则**：

| 规则   | name                  | 说明          | 默认启用 |
| ---- | --------------------- | ----------- | ---- |
| 页码过滤 | `filter_page_numbers` | 移除独立成行的页码文本 | ❌    |

**新增文件**：`cleaners/rules/page_number.py`

**页码检测正则模式**：

```python
# 纯数字行
r"^\s*\d{1,4}\s*$"
# 带横线页码
r"^\s*[-—–]\s*\d{1,4}\s*[-—–]\s*$"
# 中文页码
r"^\s*第\s*\d{1,4}\s*页\s*$"
# 英文页码
r"^\s*Page\s+\d{1,4}\s*$"
```

**API 变更**：CleanOptions 新增 `filter_page_numbers: bool = False`

***

#### Task 4：脚注/尾注处理

**目标**：识别并可选过滤文档中的脚注和尾注。

**实现策略**：

1. 基于正则模式匹配脚注标记（如 `^1`、`[1]`、`①`）
2. 检测脚注内容区域（标记后的文本直到下一个脚注或段落）
3. 可配置保留/移除/提取为元数据

**新增规则**：

| 规则   | name                | 说明              | 默认启用 |
| ---- | ------------------- | --------------- | ---- |
| 脚注处理 | `process_footnotes` | 识别脚注/尾注，可选保留或移除 | ❌    |

**新增文件**：`cleaners/rules/footnote.py`

**脚注检测模式**：

```python
# 上标数字标记
r"\[\d+\]"
r"\^\d+"
# 带圈数字
r"[①②③④⑤⑥⑦⑧⑨⑩]"
# 脚注内容行
r"^\d+\s+.+$"  # 仅在脚注区域上下文中匹配
```

**API 变更**：CleanOptions 新增 `process_footnotes: bool = False`、`footnote_action: str = "remove"`（`remove`/`keep`/`extract`）

---

#### Task 5：HTML 内容过滤

**目标**：过滤 HTML/网页文档中的噪声内容，包括导航栏、广告、页脚、侧边栏、HTML 注释、残余标签等。

**背景**：当前项目对 HTML 文档的处理仅在 `markdown_converter.py` 中通过 markdownify 的 `strip` 参数移除 4 种标签（`i`/`script`/`iframe`/`style`），缺少对 `nav`/`footer`/`header`/`aside`/`noscript` 等语义化噪声标签的处理，也缺少 HTML 实体转换、注释移除、噪声模式匹配等能力。RAGflow 在 HTML 解析阶段通过 BeautifulSoup `decompose()` 移除 8 种干扰标签，并在清洗阶段通过正则剥离残余标签和噪声内容。

**与 RAGflow 的差距**：

| 能力维度 | RAGflow | 当前项目 | 差距 |
|---------|---------|---------|------|
| 干扰标签移除 | 8 种（script/style/nav/footer/header/aside/iframe/noscript） | 4 种（script/style/iframe/i） | 缺少 nav/footer/header/aside/noscript |
| 内容区域识别 | 5 级优先级（article > main > div.content > body） | 无 | 缺少 |
| HTML 注释移除 | 支持 | 无 | 缺少 |
| HTML 实体转换 | 18 种命名实体 + 数字引用 | 依赖 markdownify 内部处理 | 可能遗漏 |
| 噪声模式匹配 | 10 种正则（版权/备案/广告等） | 无 | 缺少 |
| 分隔线/装饰线移除 | 支持 | 无 | 缺少 |

**实现策略**：分两层实现——解析层（DOM 级）和清洗层（文本级）。

##### 5.1 解析层：HTML 干扰标签移除 + 内容区域识别

在 `html_parser.py` 中增加预处理步骤，在 BeautifulSoup 解析后、返回结果前移除干扰标签并识别主要内容区域。

**干扰标签移除列表**：

| 标签 | 说明 | 移除原因 |
|------|------|---------|
| `<script>` | JavaScript 脚本 | 非文本内容，纯噪声 |
| `<style>` | CSS 样式 | 非文本内容，纯噪声 |
| `<nav>` | 导航栏 | 页面导航，非正文 |
| `<footer>` | 页脚 | 版权/备案/链接等噪声 |
| `<header>` | 页头 | 通常包含导航/Logo |
| `<aside>` | 侧边栏 | 广告/推荐/链接 |
| `<iframe>` | 嵌入框架 | 第三方内容/广告 |
| `<noscript>` | 无脚本回退 | 非正文内容 |

**内容区域识别优先级**：

| 优先级 | 选择器 | 说明 |
|--------|--------|------|
| 1 | `article` | HTML5 语义化文章标签 |
| 2 | `main` | HTML5 主要内容标签 |
| 3 | `div.content` / `div.article` / `div#content` | 常见内容区域 |
| 4 | `body` | 兜底：整个 body |

**修改文件**：`parsers/html_parser.py`

```python
# 新增参数
NOISE_TAGS = ['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']
CONTENT_SELECTORS = ['article', 'main', 'div.content', 'div.article', 'div#content']

def parse(buffer: bytes, remove_noise: bool = True, **kwargs) -> ParseResult:
    # ... 编码检测 ...
    soup = BeautifulSoup(html_str, "html.parser")

    if remove_noise:
        for tag in soup.find_all(NOISE_TAGS):
            tag.decompose()

    # 识别主要内容区域
    main_content = None
    if remove_noise:
        for selector in CONTENT_SELECTORS:
            main_content = soup.select_one(selector)
            if main_content:
                break

    content_soup = main_content if main_content else (soup.body if soup.body else soup)

    raw_text = str(soup)           # 保留完整 HTML（供 converter 使用）
    clean_text = str(content_soup) # 清洗后的 HTML（供正文提取使用）
    html_preview = str(content_soup)

    return ParseResult(
        raw_text=raw_text,
        format_text=clean_text,
        html_preview=html_preview,
        image_list=[],
    )
```

**关键设计**：`raw_text` 保留完整 HTML（供 markdownify/markitdown 转换器使用），`format_text` 存放清洗后的 HTML。转换器可根据需要选择使用哪个版本。

##### 5.2 清洗层：HTML 文本噪声过滤规则

新增 3 条 CleanRule，处理 Markdown 转换后文本中的残余 HTML 噪声。

**新增规则**：

| 规则 | name | 说明 | 默认启用 |
|------|------|------|---------|
| HTML 注释移除 | `remove_html_comments` | 移除 `<!-- ... -->` 格式的 HTML 注释 | ✅ |
| HTML 实体转换 | `normalize_html_entities` | 将 HTML 命名实体和数字引用转换为 Unicode 字符 | ✅ |
| HTML 噪声模式过滤 | `filter_html_noise` | 移除版权声明、备案信息、广告关键词等网页噪声 | ❌ |

**新增文件**：`cleaners/rules/html_clean.py`

**HTML 注释移除**：

```python
class RemoveHtmlCommentsRule(CleanRule):
    name = "remove_html_comments"
    description = "移除 HTML 注释（<!-- ... -->）"
    default_enabled = True

    _COMMENT_RE = re.compile(r"<!--[\s\S]*?-->|<!--[\s\S]*$", re.MULTILINE)

    def apply(self, text: str, **kwargs) -> str:
        return self._COMMENT_RE.sub("", text)
```

**HTML 实体转换**：

```python
class NormalizeHtmlEntitiesRule(CleanRule):
    name = "normalize_html_entities"
    description = "将 HTML 命名实体和数字引用转换为 Unicode 字符"
    default_enabled = True

    _NAMED_ENTITIES = {
        "&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">",
        "&quot;": '"', "&#39;": "'", "&apos;": "'",
        "&mdash;": "—", "&ndash;": "–", "&hellip;": "…",
        "&copy;": "©", "&reg;": "®", "&trade;": "™",
        "&lsquo;": "\u2018", "&rsquo;": "\u2019",
        "&ldquo;": "\u201c", "&rdquo;": "\u201d",
        "&deg;": "°",
    }
    _DECIMAL_RE = re.compile(r"&#(\d+);")
    _HEX_RE = re.compile(r"&#x([0-9a-fA-F]+);")

    def apply(self, text: str, **kwargs) -> str:
        for entity, char in self._NAMED_ENTITIES.items():
            text = text.replace(entity, char)
        text = self._DECIMAL_RE.sub(lambda m: chr(int(m.group(1))), text)
        text = self._HEX_RE.sub(lambda m: chr(int(m.group(1), 16)), text)
        return text
```

**HTML 噪声模式过滤**：

```python
class FilterHtmlNoiseRule(CleanRule):
    name = "filter_html_noise"
    description = "移除版权声明、备案信息、广告关键词等网页噪声"
    default_enabled = False

    BUILTIN_NOISE_PATTERNS = [
        r"copyright\s*©?\s*\d{4}.*$",
        r"all\s+rights\s+reserved.*$",
        r"[沪京粤深]ICP[备证]\d+号.*$",
        r"免责声明：.*$",
        r"本文来源：.*$",
        r"责任编辑：.*$",
        r"[浏阅]读次数[：:]\s*\d+.*$",
    ]
    BUILTIN_AD_KEYWORDS = ["广告", "推广", "优惠", "促销", "VIP", "购买", "热线"]

    def apply(self, text: str, **kwargs) -> str:
        noise_patterns = kwargs.get("html_noise_patterns", [])
        ad_keywords = kwargs.get("html_ad_keywords", [])

        all_patterns = list(self.BUILTIN_NOISE_PATTERNS) + list(noise_patterns)
        all_ads = list(self.BUILTIN_AD_KEYWORDS) + list(ad_keywords)

        lines = text.split("\n")
        result_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                result_lines.append(line)
                continue

            # 噪声模式匹配
            is_noise = False
            for pattern in all_patterns:
                if re.search(pattern, stripped, re.IGNORECASE):
                    is_noise = True
                    break

            # 广告关键词检测
            if not is_noise and all_ads:
                ad_count = sum(1 for kw in all_ads if kw in stripped)
                if ad_count > 0 and ad_count / max(len(stripped), 1) > 0.3:
                    is_noise = True

            if not is_noise:
                result_lines.append(line)

        return "\n".join(result_lines)
```

**API 变更**：CleanOptions 新增字段

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `remove_html_comments` | `bool` | `true` | 移除 HTML 注释 |
| `normalize_html_entities` | `bool` | `true` | HTML 实体转换 |
| `filter_html_noise` | `bool` | `false` | 网页噪声模式过滤 |
| `html_noise_patterns` | `list[str]` | `[]` | 自定义噪声正则模式 |
| `html_ad_keywords` | `list[str]` | `[]` | 自定义广告关键词 |

**解析层 API 变更**：`/api/parse` 新增参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `remove_html_noise` | `bool` | `true` | HTML 解析时移除干扰标签（仅 HTML 文件） |

---

#### Task 6：CleanProfile 预设机制

**目标**：建立清洗配置预设机制，按文档类型自动选择最佳清洗规则组合。

**设计**：

```python
# cleaners/profiles/base.py
class CleanProfile:
    """清洗配置预设"""
    name: str
    description: str
    rules: dict[str, bool]        # 规则启用/禁用
    params: dict[str, Any]        # 规则参数

    def to_options_dict(self) -> dict:
        """将预设转换为 CleanOptions 兼容的 dict"""
        result = {**self.rules, **self.params}
        return result

# cleaners/profiles/registry.py
_PROFILE_REGISTRY: dict[str, CleanProfile] = {}

def register_profile(profile: CleanProfile) -> None: ...
def get_profile(name: str) -> CleanProfile: ...
def get_profile_for_file(filename: str) -> CleanProfile: ...
```

**预设配置列表**：

| Profile 名      | 适用场景     | 规则差异                                                          |
| -------------- | -------- | ------------------------------------------------------------- |
| `default`      | 通用文档     | 所有默认值                                                         |
| `pdf_academic` | 学术 PDF   | 启用 filter\_toc、filter\_page\_numbers、process\_footnotes(keep) |
| `pdf_business` | 商务 PDF   | 启用 filter\_watermark、filter\_page\_numbers                    |
| `docx_report`  | DOCX 报告  | 启用 filter\_toc、process\_footnotes(keep)                       |
| `table_data`   | CSV/XLSX | 启用 clean\_table                                               |
| `legal`        | 法律文书     | 启用 filter\_toc、process\_footnotes(keep)                       |
| `web_content` | HTML 网页 | 启用 filter_watermark、filter_html_noise、clean_markdown_links |                  |

**新增文件**：

```
cleaners/profiles/
├── __init__.py
├── base.py           # CleanProfile 基类
├── registry.py       # Profile 注册表
├── default.py        # 默认配置
├── pdf_academic.py   # 学术 PDF 配置
├── pdf_business.py   # 商务 PDF 配置
├── docx_report.py    # DOCX 报告配置
├── table_data.py     # 表格数据配置
├── legal.py          # 法律文书配置
└── web_content.py    # 网页内容配置
```

##### 5.1 Profile 与手动选项冲突解决方案

**核心原则：Options 是唯一真相来源，Profile 只是前端填充模板。**

冲突的本质：用户选择预设后又手动修改选项，系统应听谁的？

**三种方案对比**：

| 方案               | 思路                                     | 优势   | 劣势                       |
| ---------------- | -------------------------------------- | ---- | ------------------------ |
| A. Profile 优先    | Profile 强制覆盖，手动修改无效                    | 一致性强 | 用户困惑：改了没效果               |
| B. Options 优先    | Options 始终是最终值，Profile 只是填充模板          | 简单直观 | API 用户无法仅靠 profile 名使用预设 |
| C. Optional 显式覆盖 | 区分"未设置"和"显式设置为 False"，Profile 填充未设置的字段 | 精确控制 | 实现复杂，破坏向后兼容              |

**采用方案 B + 前端状态管理 + 后端可选 Profile 支持**。

**不采用方案 C 的原因**：

1. 需将所有 `CleanOptions` 字段改为 `bool | None = None`，破坏现有 API 调用方的默认值依赖
2. `CleanPipeline.should_run()` 需额外处理 `None` 值
3. 前端序列化需区分 `null`（未设置）和 `false`（显式关闭），增加复杂度

**前端设计**：

```js
// Profile 定义（前端常量，与后端 profiles 保持同步）
const CLEAN_PROFILES = {
  default: {
    label: '默认',
    options: { trim: true, normalize_unicode: true, /* ...全部默认值... */ }
  },
  pdf_academic: {
    label: '学术论文 PDF',
    options: { /* ... */ filter_toc: true, filter_page_numbers: true,
               process_footnotes: true, footnote_action: 'keep' }
  },
  // ...
}

const selectedProfile = ref('default')

// 选择 profile 时：全量填充 cleanOptions
function applyProfile(profileName) {
  const profile = CLEAN_PROFILES[profileName]
  if (profile) {
    Object.assign(cleanOptions.value, JSON.parse(JSON.stringify(profile.options)))
    selectedProfile.value = profileName
  }
}

// 监听 cleanOptions 变化：任何手动修改 → 切换为"自定义"
watch(cleanOptions, (newVal) => {
  const currentProfile = CLEAN_PROFILES[selectedProfile.value]
  if (currentProfile && !isOptionsEqual(newVal, currentProfile.options)) {
    selectedProfile.value = 'custom'
  }
}, { deep: true })

function isOptionsEqual(a, b) {
  return Object.keys(b).every(key => a[key] === b[key])
}
```

**后端设计**：

```python
class CleanRequest(BaseModel):
    text: str
    options: CleanOptions = Field(default_factory=CleanOptions)
    profile: str = "default"  # 可选：预设配置名

@app.post("/api/clean", response_model=CleanResponse)
async def clean(req: CleanRequest):
    opts = req.options.model_dump()
    default_opts = CleanOptions().model_dump()

    # 仅当 options 全为默认值且 profile 非 default 时，用 profile 覆盖
    if opts == default_opts and req.profile != "default":
        profile = get_profile(req.profile)
        if profile:
            opts = profile.to_options_dict()

    cleaned = clean_text(req.text, opts)
    return CleanResponse(cleaned=cleaned)
```

**合并规则**：`options` 有任何非默认值 → 忽略 profile，options 完全优先。

**数据流场景**：

| 场景                    | 用户操作                                                                       | 前端发送                            | 后端行为                       |
| --------------------- | -------------------------------------------------------------------------- | ------------------------------- | -------------------------- |
| 前端选预设不修改              | 选择 "pdf\_academic"                                                         | 完整 options（含 filter\_toc=True）  | 直接执行                       |
| 前端选预设后修改              | 选择 "pdf\_academic" → 取消 filter\_toc                                        | 完整 options（含 filter\_toc=False） | 直接执行                       |
| API 仅指定 profile       | `{"text":"...", "profile":"pdf_academic"}`                                 | —                               | options 全默认 → 用 profile 覆盖 |
| API 指定 profile + 部分覆盖 | `{"text":"...", "profile":"pdf_academic", "options":{"filter_toc":false}}` | —                               | options 有非默认值 → options 优先 |

**UI 交互**：

1. 清洗选项顶部新增「清洗预设」下拉选择器
2. 选择预设后自动填充所有规则配置
3. 用户手动修改任一规则 → 预设选择器切换为「自定义」
4. 预设选择器选项：默认 / 学术论文 PDF / 商务 PDF / DOCX 报告 / 表格数据 / 法律文书 / 网页内容 / 自定义

***

#### Task 7：清洗与转换解耦

**目标**：消除 `markdown_converter.py` 与 `cleaners/` 模块的逻辑重复。

**当前问题**：

- `markdown_converter.py` 中的 `simple_text()` 有一套完整的清洗逻辑
- `cleaners/` 模块有另一套基于 CleanRule 的清洗逻辑
- 两者行为应保持一致但代码重复

**修改方案**：

1. `markdown_converter.py` 中的 `simple_text()` 改为委托调用 `cleaners.text_cleaner.simple_text()`
2. `fastgpt_simple_text()` 保持不变（固定规则集的快捷方式，用于分块器）
3. `simple_markdown_text()` 改为调用 pipeline + markdown\_post 规则
4. `_simple_text()` 在 `text_chunker.py` 中保持不变（轻量规范化，性能优先）

**修改文件**：

- `converters/markdown_converter.py` — `simple_text()` 委托 cleaners
- `cleaners/text_cleaner.py` — 确保导出一致

***

#### Task 8：前端 UI 更新

**目标**：在 Demo 前端中支持 CleanProfile 预设选择和新增规则配置。

**UI 变更**：

1. 新增「清洗预设」下拉选择器（在清洗选项顶部）
2. 新增 P2 规则的 checkbox 控件（目录过滤、页码过滤、脚注处理）
3. 选择预设后自动填充对应的规则配置
4. 用户手动修改规则后，预设选择器切换为「自定义」

**修改文件**：`KnowledgeProcessDemo.vue`

***

#### Task 9：集成测试和回归验证

**目标**：确保 P2 变更不破坏现有功能。

**测试项**：

1. 运行完整测试套件 `pytest tests/ -v`
2. 验证 CleanProfile 预设正确加载和应用
3. 验证新增规则的独立功能
4. 验证 `simple_text()` 委托后的行为一致性
5. 验证前端 Demo 全流程

### 3.3 P2 文件变更清单

| 文件路径                                | 变更类型 | 变更摘要                               |
| ----------------------------------- | ---- | ---------------------------------- |
| `cleaners/rules/markdown_post.py`   | 新增   | Markdown 后处理规则（3 个 Rule）           |
| `cleaners/rules/toc_filter.py`      | 新增   | 目录区域过滤规则                           |
| `cleaners/rules/page_number.py`     | 新增   | 页码过滤规则                             |
| `cleaners/rules/footnote.py`        | 新增   | 脚注/尾注处理规则                          |
| `cleaners/rules/html_clean.py`      | 新增   | HTML 清洗规则（3 个 Rule：注释移除、实体转换、噪声过滤） |
| `cleaners/rules/__init__.py`        | 修改   | 注册新规则                              |
| `cleaners/profiles/__init__.py`     | 新增   | Profile 模块导出                       |
| `cleaners/profiles/base.py`         | 新增   | CleanProfile 基类                    |
| `cleaners/profiles/registry.py`     | 新增   | Profile 注册表                        |
| `cleaners/profiles/default.py`      | 新增   | 默认配置                               |
| `cleaners/profiles/pdf_academic.py` | 新增   | 学术 PDF 配置                          |
| `cleaners/profiles/pdf_business.py` | 新增   | 商务 PDF 配置                          |
| `cleaners/profiles/docx_report.py`  | 新增   | DOCX 报告配置                          |
| `cleaners/profiles/table_data.py`   | 新增   | 表格数据配置                             |
| `cleaners/profiles/legal.py`        | 新增   | 法律文书配置                             |
| `cleaners/profiles/web_content.py`  | 新增   | 网页内容配置                             |
| `cleaners/text_cleaner.py`          | 修改   | 支持 Profile                         |
| `cleaners/__init__.py`              | 修改   | 更新导出                               |
| `parsers/html_parser.py`            | 修改   | 新增干扰标签移除 + 内容区域识别                  |
| `converters/markdown_converter.py`  | 修改   | simple\_text() 委托 cleaners         |
| `app.py`                            | 修改   | CleanOptions 新增 P2 字段 + profile + remove\_html\_noise 参数 |
| `KnowledgeProcessDemo.vue`          | 修改   | 新增预设选择器 + P2 规则控件 + HTML 选项       |
| `tests/test_markdown_post_rule.py`  | 新增   | Markdown 后处理规则测试                   |
| `tests/test_toc_filter_rule.py`     | 新增   | 目录过滤规则测试                           |
| `tests/test_page_number_rule.py`    | 新增   | 页码过滤规则测试                           |
| `tests/test_footnote_rule.py`       | 新增   | 脚注处理规则测试                           |
| `tests/test_html_clean_rule.py`     | 新增   | HTML 清洗规则测试                        |
| `tests/test_html_parser_noise.py`   | 新增   | HTML 解析器噪声移除测试                     |
| `tests/test_clean_profile.py`       | 新增   | CleanProfile 预设测试                  |

### 3.4 P2 完成后的规则执行顺序

```
trim → normalize_unicode → remove_invisible_chars → remove_chinese_space
→ normalize_newline → fix_hyphenation → collapse_whitespace → remove_empty_lines
→ remove_html_comments → normalize_html_entities → filter_html_noise
→ filter_watermark → filter_toc → filter_page_numbers → process_footnotes
→ deduplicate_paragraphs → clean_table → clean_markdown_links → remove_md_escapes
→ clean_md_structure → mask_sensitive → filter_special_chars → 控制字符替换
```

### 3.5 P2 完成后的 CleanOptions 完整字段

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
  "remove_html_comments": true,
  "normalize_html_entities": true,
  "filter_html_noise": false,
  "html_noise_patterns": [],
  "html_ad_keywords": [],
  "filter_watermark": false,
  "watermark_keywords": [],
  "watermark_min_repeat": 2,
  "watermark_max_line_length": 30,
  "filter_toc": false,
  "filter_page_numbers": false,
  "process_footnotes": false,
  "footnote_action": "remove",
  "deduplicate_paragraphs": false,
  "dedup_fuzzy": false,
  "dedup_fuzzy_threshold": 0.9,
  "clean_table": false,
  "clean_markdown_links": true,
  "remove_md_escapes": true,
  "clean_md_structure": true,
  "mask_sensitive": false,
  "filter_special_chars": false
}
```

***

## 4. P3 实施计划：专用分块策略 + 语义增强

### 4.1 P3 目标

1. 实现文档类型专用分块策略（对标 RAGflow 的 10 种分块方法）
2. 引入 LLM 驱动的语义增强能力（摘要/关键词/问题生成）

### 4.2 专用分块策略

| 分块方法   | 标识符            | 说明                                      |  优先级 |
| ------ | -------------- | --------------------------------------- | :--: |
| 论文分块   | `paper`        | 按 Section/Abstract/Introduction 等论文结构分块 | P3-a |
| 书籍分块   | `book`         | 按章节（Chapter/Section）分块                  | P3-a |
| 法律文书分块 | `laws`         | 按条款（条/款/项）分块                            | P3-b |
| QA 分块  | `qa`           | 按 Q\&A 对分块                              | P3-b |
| 表格分块   | `table`        | 按表格行为单位分块                               | P3-a |
| 演示文稿分块 | `presentation` | 按 Slide 分块                              | P3-c |
| 简历分块   | `resume`       | 按简历结构分块                                 | P3-c |
| 整篇分块   | `one`          | 整篇文档作为一个块                               | P3-a |

**新增目录**：

```
chunkers/
├── strategies/
│   ├── __init__.py
│   ├── base.py           # ChunkStrategy 基类
│   ├── paper.py          # 论文分块策略
│   ├── book.py           # 书籍分块策略
│   ├── laws.py           # 法律文书分块策略
│   ├── qa.py             # QA 分块策略
│   ├── table.py          # 表格分块策略
│   ├── presentation.py   # 演示文稿分块策略
│   ├── resume.py         # 简历分块策略
│   └── one.py            # 整篇分块策略
```

### 4.3 语义增强（Transformer）

**架构设计**：

```
transformers/
├── __init__.py
├── base.py              # Transformer 基类
├── summary.py           # 摘要生成
├── keywords.py          # 关键词提取
├── questions.py         # 问题生成
├── metadata.py          # 元数据生成
└── llm_backend.py       # LLM 后端抽象
```

**LLM 后端支持**：

- OpenAI API（GPT-4o-mini 等）
- 本地模型（Ollama / vLLM）
- 其他兼容 API

**三种增强模式**：

- **Improvise**：创造性增强，生成更丰富的摘要和问题
- **Precise**：精确增强，严格基于原文内容
- **Balance**：平衡模式（默认）

**API 变更**：

```python
class TransformRequest(BaseModel):
    text: str
    tasks: list[str] = ["summary"]  # summary / keywords / questions / metadata
    mode: str = "balance"           # improvise / precise / balance
    llm_config: dict = {}           # LLM 后端配置
```

***

## 5. P4 实施计划：版面分析模型集成

### 5.1 P4 目标

集成 DeepDoc 或类似版面分析模型，实现基于视觉理解的文档结构识别。

### 5.2 核心能力

| 能力     | 说明                    |
| ------ | --------------------- |
| 版面区域检测 | 识别标题/段落/表格/图片/页眉/页脚区域 |
| 阅读顺序排列 | 按人类阅读习惯排列区域           |
| 表格结构识别 | 识别合并单元格、表头、数据区域       |
| OCR    | 图片/扫描件文字识别            |
| 公式识别   | 数学公式提取                |

### 5.3 技术选型

| 方案                     | 优势      | 劣势       |
| ---------------------- | ------- | -------- |
| RAGflow DeepDoc        | 成熟、功能完整 | 依赖重、部署复杂 |
| MinerU (已集成)           | 已有集成    | 版面分析能力有限 |
| PaddleOCR + LayoutLMv3 | 轻量、可定制  | 需自行集成    |
| 云端 API (百度/腾讯)         | 零部署     | 成本、隐私    |

***

## 6. 实施路线图总览

```
Phase 1 (P0) ✅ 已完成 ─── 基础清洗规则补齐
  ├── 扩展控制字符范围
  ├── PDF 页眉页脚过滤可配置化
  ├── 连字符断行修复
  ├── Unicode NFKC 标准化
  ├── 不可见字符移除
  ├── 敏感信息脱敏
  └── 特殊字符过滤

Phase 2 (P1) ✅ 已完成 ─── 结构级清洗规则
  ├── CleanRule 基类和注册机制
  ├── 水印文本过滤
  ├── 重复段落去重
  ├── 表格清洗
  ├── 脱敏增强（银行卡/护照/军官证）
  └── 前端 UI + tooltip

Phase 3 (P2) 📋 本期规划 ─── 文档类型感知清洗 + HTML 过滤
  ├── Markdown 后处理规则化
  ├── 目录区域过滤
  ├── 页码过滤
  ├── 脚注/尾注处理
  ├── HTML 内容过滤（干扰标签移除 + 内容区域识别 + 实体转换 + 注释移除 + 噪声模式过滤）
  ├── CleanProfile 预设机制
  ├── 清洗与转换解耦
  └── 前端 UI 更新

Phase 4 (P3) 🔮 远期规划 ─── 专用分块 + 语义增强
  ├── 文档类型专用分块策略
  ├── LLM 语义增强（摘要/关键词/问题）
  └── Transformer Pipeline

Phase 5 (P4) 🔮 远期规划 ─── 版面分析模型
  ├── DeepDoc / LayoutLMv3 集成
  ├── 基于视觉理解的文档结构识别
  └── OCR + 公式识别
```

***

## 7. 风险评估

| 风险项                  | 等级   | 说明                      | 缓解措施                    |
| -------------------- | ---- | ----------------------- | ----------------------- |
| 目录过滤误删正文             | 🟡 中 | 目录模式可能匹配到合法的编号列表        | 默认关闭，需 ≥3 行连续匹配         |
| 页码过滤误删               | 🟢 低 | 独立数字行可能包含合法内容           | 仅过滤纯数字行，保留含文字的行         |
| 脚注处理破坏引用             | 🟡 中 | 移除脚注可能导致正文引用标记孤立        | 提供 keep/extract 选项      |
| HTML 干扰标签误删正文内容      | 🟡 中 | header/footer/aside 可能包含有用信息 | 默认启用但可关闭；raw_text 保留完整 HTML |
| HTML 内容区域识别失败        | 🟢 低 | 部分网页无语义化标签，无法识别主内容区     | 兜底使用 body，不影响解析         |
| HTML 实体转换误转换          | 🟢 低 | 已转义的实体被二次转换             | 仅转换未还原的实体，NFKC 已处理部分    |
| HTML 噪声模式误删正文         | 🟡 中 | 噪声正则可能匹配合法内容            | 默认关闭，关键词密度阈值 30%        |
| CleanProfile 与手动选项冲突 | 🟡 中 | 用户选预设后又手动修改             | 手动修改后切换为「自定义」           |
| 解耦引入回归               | 🟠 中 | simple\_text() 委托可能改变行为 | 严格回归测试                  |
| 专用分块策略复杂度            | 🔴 高 | 每种文档类型需要独立的分块逻辑         | 渐进实现，优先 paper/book/laws |
| LLM 语义增强成本           | 🔴 高 | API 调用成本和延迟             | 可配置后端，支持本地模型            |

***

## 8. 向后兼容性保证

| 验证项                                       | 预期结果           |
| ----------------------------------------- | -------------- |
| `simple_text("  hello  world  \n\n\n  ")` | 与 P1 行为一致      |
| `fastgpt_simple_text(...)`                | 行为不变           |
| `simple_markdown_text(...)`               | 行为不变（委托后输出一致）  |
| `/api/clean` 端点默认参数                       | 输出与 P1 一致      |
| 所有 P2 新增字段默认关闭                            | 不影响现有行为        |
| `profile="default"`                       | 等同于不指定 profile |

