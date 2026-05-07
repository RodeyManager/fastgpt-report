# Code Wiki - FastGPT 文档处理流水线项目

## 项目概览

### 项目名称与简介

**FastGPT 源码分析报告与文档处理流水线 Demo** 是一个 monorepo 项目，包含 Vue 3 分析报告 Web 应用和 Python FastAPI 后端 API，用于复刻 FastGPT 知识库的文档处理链路。

### 项目地址

| 组件 | 地址 |
|------|------|
| 前端（报告 + Demo） | `https://rodeymanager.github.io/fastgpt-report/` |
| 后端 API | `https://huggingface.co/spaces/RodeyManager/knowledge-process-api` |

---

## 项目结构

```
/workspace/
├── apps/                              # Vue 前端应用集合
│   ├── fastgpt-report/                # FastGPT 源码分析报告（13 章节）
│   ├── maxkb-report/                  # MaxKB 源码分析报告
│   ├── ragflow-report/                 # RagFlow 源码分析报告
│   └── knowledge-process-demo/        # 文档处理 Demo 前端
├── knowledge-process-api/              # Python FastAPI 后端
│   ├── src/fastgpt_demo/              # 核心业务逻辑
│   │   ├── parsers/                   # 文档解析器
│   │   ├── converters/                # Markdown 转换器
│   │   ├── cleaners/                  # 文本清洗器
│   │   ├── chunkers/                  # 文本分块器
│   │   └── indexers/                  # 图片索引器
│   ├── tests/                         # pytest 测试套件
│   ├── app.py                         # FastAPI 应用入口
│   └── pyproject.toml                 # Python 依赖配置
├── packages/                          # 共享包（预留）
├── pnpm-workspace.yaml                # pnpm monorepo 配置
└── package.json                       # 根目录 npm 脚本
```

---

## 技术栈

### 前端技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue 3 | ^3.4.0 |
| 构建工具 | Vite | ^5.4.0 |
| 路由 | vue-router | ^4.3.0 |
| 图表 | ECharts + vue-echarts | ^5.5.0 / ^7.0.0 |
| 测试 | vitest + @vue/test-utils | ^2.0.0 / ^2.4.0 |
| 文档解析（前端） | mammoth, pdfjs-dist, papaparse, xlsx | - |

### 后端技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 框架 | FastAPI | ^0.115.0 |
| 服务器 | uvicorn | ^0.30.0 |
| PDF 解析 | PyMuPDF (pymupdf) | ^1.24.0 |
| DOCX 解析 | mammoth | ^1.8.0 |
| Excel 解析 | openpyxl | ^3.1.0 |
| PPTX 解析 | python-pptx | ^1.0.0 |
| Markdown 转换 | markdownify, markitdown | ^0.14.0 |
| HTML 解析 | beautifulsoup4 | ^4.12.0 |
| 编码检测 | chardet | ^5.0.0 |
| 图片处理 | Pillow | ^10.0.0 |
| HTTP 客户端 | httpx | ^0.28.1 |
| 测试 | pytest | ^9.0.3 |

### 包管理

- **pnpm**: 前端 monorepo 包管理
- **uv**: Python 依赖管理

---

## 模块架构

### 模块职责总览

```
┌─────────────────────────────────────────────────────────────┐
│                    API 网关层 (app.py)                       │
├─────────────────────────────────────────────────────────────┤
│  /api/parse  │  /api/convert  │  /api/clean  │  /api/chunk  │
└──────────────┴─────────────────┴──────────────┴─────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                     核心业务模块                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   parsers/   │  │  converters/ │  │  cleaners/    │     │
│  │   文档解析    │  │  Markdown转换│  │   文本清洗    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  chunkers/  │  │  indexers/   │                        │
│  │   文本分块   │  │   图片索引    │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### 模块依赖关系图

```
parsers/__init__.py      converters/__init__.py
        │                         │
        ▼                         ▼
   _types.py              markdown_converter.py
   pdf_parser.py           markitdown_converter.py
   docx_parser.py
   csv_parser.py           cleaners/__init__.py
   xlsx_parser.py                   │
   pptx_parser.py                   ▼
   html_parser.py           text_cleaner.py (调用 converters)
   text_parser.py
   mineru_parser.py
         │
         ▼
   chunkers/__init__.py ───► text_chunker.py
         │
         ▼
   indexers/__init__.py ───► image_indexer.py
```

---

## 核心模块详解

### 1. parsers - 文档解析器模块

**文件位置**: `/knowledge-process-api/src/fastgpt_demo/parsers/`

#### 1.1 `_types.py` - 数据类型定义

```python
@dataclass
class ParseResult:
    raw_text: str              # 原始提取文本
    format_text: str           # 格式化后的文本
    html_preview: str          # HTML 预览内容
    image_list: list           # 图片列表
    sheet_names: Optional[list[str]]  # Excel 工作表名称
```

#### 1.2 `__init__.py` - 解析器调度中心

**关键函数**: `parse_file(buffer, filename, method, engine)`

根据文件扩展名和引擎类型自动分发到对应的解析器。

| 支持的格式 | 解析器 | 引擎 |
|-----------|--------|------|
| `.pdf` | pdf_parser | fastgpt/mineru |
| `.docx` | docx_parser | fastgpt/mineru |
| `.csv` | csv_parser | fastgpt |
| `.xlsx` | xlsx_parser | fastgpt |
| `.pptx` | pptx_parser | fastgpt/mineru |
| `.txt/.md` | text_parser | fastgpt |
| `.html/.htm` | html_parser | fastgpt |
| 图片格式 | mineru_parser | mineru |

#### 1.3 `pdf_parser.py` - PDF 解析器

**核心函数**: `parse(buffer) -> ParseResult`

使用 PyMuPDF 库解析 PDF 文件：
- 逐页提取文本内容
- 过滤页眉页脚区域（顶部/底部 5%）
- 检测句子结束符（`.。！？；! ?`）并添加换行
- 返回原始文本、格式化文本和 HTML 预览

**关键辅助函数**: `_extract_page_text(page)`
- 遍历 PDF 页面的文字块
- 根据 Y 轴位置过滤页眉页脚
- 构建带有语义断句的文本输出

#### 1.4 `docx_parser.py` - DOCX 解析器

**核心函数**: `parse(buffer) -> ParseResult`

使用 mammoth 库解析 DOCX 文件：
- `mammoth.convert_to_html()`: 转换为 HTML（用于预览）
- `mammoth.extract_raw_text()`: 提取纯文本
- 返回原始文本、HTML 预览和图片列表

#### 1.5 `mineru_parser.py` - MinerU 解析器

**核心函数**: `parse(buffer, filename) -> ParseResult`

MinerU 高质量解析引擎的包装器：
- 支持的格式: PDF, DOCX, DOC, PPTX, PNG, JPG, JPEG, GIF, WEBP
- 检查 `MINERU_API_URL` 环境变量
- 有 API 时调用真实 API
- 无 API 时返回占位符数据

**环境变量**:
| 变量名 | 说明 |
|--------|------|
| `MINERU_API_URL` | MinerU API 服务地址 |

### 2. converters - Markdown 转换器模块

**文件位置**: `/knowledge-process-api/src/fastgpt_demo/converters/`

#### 2.1 `markdown_converter.py` - 主转换器

**核心函数**:

| 函数名 | 说明 |
|--------|------|
| `html_to_markdown(html)` | HTML 转 Markdown |
| `convert_to_markdown(raw_text, format_text, file_ext)` | 根据扩展名路由转换 |
| `convert_to_markdown_multi(...)` | 多工具对比转换 |
| `fastgpt_simple_text(text)` | 基础文本清理 |
| `simple_markdown_text(raw_text)` | Markdown 专用清理 |
| `simple_text(text, options)` | 可配置文本清理 |

**支持的转换工具**: `markdownify`, `markitdown`

**文件类型处理**:
- `.docx/.doc`: HTML → Markdown
- `.csv/.xlsx/.xls`: 使用预格式化的表格 Markdown
- `.md`: 直接返回原始内容
- `.html`: HTML → Markdown
- 其他: 直接返回原始文本

#### 2.2 `markitdown_converter.py` - Markitdown 转换器

提供备选的 HTML → Markdown 转换实现。

### 3. cleaners - 文本清洗器模块

**文件位置**: `/knowledge-process-api/src/fastgpt_demo/cleaners/`

#### 3.1 `text_cleaner.py`

```python
clean_text = simple_text  # 别名，调用 converters 中的实现
```

**清洗选项** (CleanOptions):

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `trim` | true | 去除首尾空白 |
| `remove_chinese_space` | true | 移除中文字符间空格 |
| `normalize_newline` | true | 规范化换行符 |
| `collapse_whitespace` | true | 合并多余空格 |
| `remove_empty_lines` | true | 移除空行 |

### 4. chunkers - 文本分块器模块

**文件位置**: `/knowledge-process-api/src/fastgpt_demo/chunkers/`

#### 4.1 `text_chunker.py` - 递归多级分块器

**核心函数**: `split_text_2_chunks(text, chunk_size, overlap_ratio, paragraph_chunk_deep, ...)`

这是 FastGPT 递归多级分块算法的 1:1 Python 移植版本。

**参数说明**:

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `text` | - | 待分块文本 |
| `chunk_size` | 500 | 目标块大小 |
| `overlap_ratio` | 0.15 | 重叠率 |
| `paragraph_chunk_deep` | 5 | Markdown 标题级别深度 |
| `max_size` | 8000 | 单块最大字符数 |

**分块策略优先级**（从高到低）:

1. **自定义正则分割** (custom_reg)
2. **Markdown 标题分割** (H1-H5)
3. **代码块分割** (```)
4. **Markdown 表格分割**
5. **双换行符分割** (段落)
6. **单换行符分割**
7. **句子分割** (。.!？；,)

**核心辅助函数**:

| 函数名 | 说明 |
|--------|------|
| `get_text_valid_length(text)` | 计算有效字符数（不含空白） |
| `str_is_md_table(text)` | 检测是否为 Markdown 表格 |
| `markdown_table_split(text, chunk_size)` | 表格分割（保留表头） |
| `common_split(text, chunk_size, ...)` | 核心递归分块算法 |
| `_simple_text(text)` | 最终文本规范化 |

**返回值**:
```python
{
    "chunks": list[str],  # 分块后的文本列表
    "chars": int          # 总字符数
}
```

### 5. indexers - 图片索引器模块

**文件位置**: `/knowledge-process-api/src/fastgpt_demo/indexers/`

#### 5.1 `image_indexer.py`

**类**: `ImageIndexer`

**方法**:

| 方法名 | 说明 |
|--------|------|
| `load_image(buffer, filename)` | 从字节加载图片并提取元数据 |
| `get_vlm_description()` | 获取 VLM 描述文本（静态） |

**支持的图片格式**: PNG, JPG, JPEG, GIF, WEBP, SVG, BMP

**load_image 返回值**:
```python
{
    "preview": Image,      # PIL Image 对象
    "width": int,          # 宽度
    "height": int,         # 高度
    "format": str,         # 格式名称
    "size_bytes": int,     # 文件大小
    "is_image": bool       # 是否为有效图片
}
```

---

## API 接口规范

### 基地址

```
本地开发: http://localhost:8000
生产环境: https://rodeymanager-knowledge-process-api.hf.space
```

### 接口列表

#### 1. 健康检查

```
GET /api/health
```

**响应**:
```json
{
    "status": "ok"
}
```

#### 2. 文档解析

```
POST /api/parse
Content-Type: multipart/form-data
```

**请求参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `file` | File | 必填 | 上传的文件 |
| `method` | string | "auto" | 解析方法（见下方） |
| `engine` | string | "fastgpt" | 解析引擎（fastgpt/mineru） |

**method 可选值**:
| 值 | 说明 |
|------|------|
| `auto` | 根据扩展名自动选择（推荐） |
| `pdf` | PDF 解析 |
| `docx` | DOCX 解析 |
| `csv` | CSV 解析 |
| `xlsx` | XLSX 解析 |
| `pptx` | PPTX 解析 |
| `text` | 纯文本解析 |
| `html` | HTML 解析 |

**响应**:
```json
{
    "raw_text": "原始提取文本",
    "format_text": "格式化文本",
    "html_preview": "<pre>HTML预览</pre>",
    "image_list": [],
    "sheet_names": ["Sheet1", "Sheet2"]
}
```

#### 3. Markdown 转换

```
POST /api/convert
Content-Type: application/json
```

**请求体**:
```json
{
    "raw_text": "原始文本或HTML",
    "format_text": "格式化文本",
    "file_ext": ".docx",
    "tools": ["markitdown"]
}
```

**响应**:
```json
{
    "results": [
        {
            "tool": "markitdown",
            "markdown": "转换后的Markdown",
            "note": "转换说明",
            "duration_ms": 125.5
        }
    ]
}
```

#### 4. 文本清洗

```
POST /api/clean
Content-Type: application/json
```

**请求体**:
```json
{
    "text": "待清洗文本",
    "options": {
        "trim": true,
        "remove_chinese_space": true,
        "normalize_newline": true,
        "collapse_whitespace": true,
        "remove_empty_lines": true
    }
}
```

**响应**:
```json
{
    "cleaned": "清洗后的文本"
}
```

#### 5. 文本分块

```
POST /api/chunk
Content-Type: application/json
```

**请求体**:
```json
{
    "text": "待分块文本",
    "chunk_size": 500,
    "overlap_ratio": 0.2,
    "paragraph_chunk_deep": 2
}
```

**响应**:
```json
{
    "chunks": ["块1", "块2", "块3"],
    "chars": 1500
}
```

#### 6. 图片索引

```
POST /api/index-image
Content-Type: multipart/form-data
```

**请求参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `file` | File | 上传的图片文件 |

**响应**:
```json
{
    "description": "图片描述（VLM生成）",
    "width": 1920,
    "height": 1080,
    "format": "PNG",
    "size_bytes": 102400
}
```

---

## 前端应用

### 1. fastgpt-report - FastGPT 源码分析报告

**位置**: `/workspace/apps/fastgpt-report/`

13 章节 Vue 3 分析报告应用，使用 ECharts 可视化展示源码架构。

**章节结构**:

| 章节 | 组件 | 说明 |
|------|------|------|
| 1 | Section1Overview.vue | 项目概览 |
| 2 | Section2Architecture.vue | 架构设计 |
| 3 | Section3Upload.vue | 文档上传与解析 |
| 4 | Section4Cleaning.vue | 数据清洗 |
| 5 | Section5Chunking.vue | 文本分块 |
| 6 | Section6Image.vue | 图片索引与 VLM |
| 7 | Section7Embedding.vue | 向量嵌入 |
| 8 | Section8Retrieval.vue | 检索与召回 |
| 9 | Section9Training.vue | 训练与微调 |
| 10 | Section10Summary.vue | 总结与展望 |
| 11 | Section11Schemas.vue | 数据库 Schema |
| 12 | Section12Dependencies.vue | 依赖关系分析 |
| 13 | Section13ArchitectureDetail.vue | 架构细节 |

**共享组件**:
- `Sidebar.vue`: 侧边导航栏
- `global.css`: 全局样式

**路由**: `/workspace/apps/fastgpt-report/src/router/index.js`

### 2. maxkb-report - MaxKB 源码分析报告

**位置**: `/workspace/apps/maxkb-report/`

MaxKB 知识库系统的源码分析报告，10 章节结构。

**章节结构**:

| 章节 | 组件 | 说明 |
|------|------|------|
| 1 | Section1Overview.vue | 项目概览 |
| 2 | Section2Knowledge.vue | 知识库管理 |
| 3 | Section3Upload.vue | 文档上传 |
| 4 | Section4Parsing.vue | 文档解析 |
| 5 | Section5Cleaning.vue | 数据清洗 |
| 6 | Section6Chunking.vue | 文本分块 |
| 7 | Section7Embedding.vue | 向量嵌入 |
| 8 | Section8Retrieval.vue | 检索系统 |
| 9 | Section9E2EFlow.vue | 端到端流程 |
| 10 | Section10Summary.vue | 总结 |

### 3. ragflow-report - RagFlow 源码分析报告

**位置**: `/workspace/apps/ragflow-report/`

RagFlow 检索增强生成系统的源码分析报告，14 章节结构。

**章节结构**:

| 章节 | 组件 | 说明 |
|------|------|------|
| 1 | Section1Overview.vue | 项目概览 |
| 2 | Section2Knowledge.vue | 知识库管理 |
| 3 | Section3Upload.vue | 文档上传 |
| 4 | Section4DeepDoc.vue | DeepDoc 解析 |
| 5 | Section5Cleaning.vue | 数据清洗 |
| 6 | Section6Chunking.vue | 文本分块 |
| 7 | Section7Embedding.vue | 向量嵌入 |
| 8 | Section8Retrieval.vue | 检索系统 |
| 9 | Section9Summary.vue | 总结 |
| 10 | Section10Comparison.vue | 方案对比 |
| 11 | Section11Etl.vue | ETL 流程 |
| 12 | Section12HybridSearch.vue | 混合搜索 |
| 13 | Section13Agent.vue | Agent 系统 |
| 14 | Section14Solutions.vue | 解决方案 |

### 4. knowledge-process-demo - 文档处理 Demo

**位置**: `/workspace/apps/knowledge-process-demo/`

交互式文档处理流水线 Demo 前端，5 步流程可视化。

**流水线步骤**:

```
Step 0: 文档解析 → Step 1: Markdown转换 → Step 2: 数据清洗
                                                        ↓
Step 4: 图片索引 ← Step 3: 文本分块
```

---

## 依赖关系分析

### 前端依赖

```
fastgpt-report/
├── vue@^3.4.0                    # Vue 核心
├── vue-router@^4.3.0             # 路由
├── echarts@^5.5.0                # 图表库
├── vue-echarts@^7.0.0           # Vue-ECharts 绑定
├── markdown-it@^14.0.0          # Markdown 解析
├── turndown@^7.2.4              # HTML→Markdown 转换
├── mammoth@^1.12.0              # DOCX 解析（前端）
├── pdfjs-dist@^5.6.205          # PDF 渲染
├── papaparse@^5.5.3             # CSV 解析
├── xlsx@^0.18.5                 # Excel 处理
└── joplin-turndown-plugin-gfm@^1.0.12  # GFM 插件
```

### 后端依赖

```
knowledge-process-api/
├── fastapi@^0.115.0              # Web 框架
├── uvicorn@^0.30.0               # ASGI 服务器
├── pymupdf@^1.24.0               # PDF 处理
├── mammoth@^1.8.0               # DOCX 处理
├── openpyxl@^3.1.0              # Excel 处理
├── python-pptx@^1.0.0           # PPT 处理
├── markdownify@^0.14.0          # HTML→Markdown
├── markitdown@^1.0.0            # 备选转换器
├── beautifulsoup4@^4.12.0        # HTML 解析
├── chardet@^5.0.0               # 编码检测
├── Pillow@^10.0.0               # 图片处理
└── httpx@^0.28.1                # HTTP 客户端
```

---

## 项目运行方式

### 环境要求

| 组件 | 要求 |
|------|------|
| Node.js | >= 16.x |
| pnpm | >= 8.x |
| Python | >= 3.10 |
| uv | 最新版 |

### 本地开发

#### 1. 安装依赖

```bash
# 前端依赖
pnpm install

# 后端依赖
cd knowledge-process-api
uv sync
```

#### 2. 启动开发服务器

```bash
# 启动所有前端应用
pnpm dev

# 单独启动各应用
pnpm dev:demo       # 文档处理 Demo
pnpm dev:ragflow    # RagFlow 报告
pnpm dev:maxkb      # MaxKB 报告

# 启动后端 API
cd knowledge-process-api
uv run uvicorn app:app --reload --port 8000
```

#### 3. 访问地址

| 服务 | 地址 |
|------|------|
| FastGPT 分析报告 | http://localhost:5173 |
| 文档处理 Demo | http://localhost:3001 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

### 构建

```bash
# 构建所有前端应用
pnpm build

# 单独构建
pnpm build:demo      # 文档处理 Demo
pnpm build:ragflow   # RagFlow 报告
pnpm build:maxkb     # MaxKB 报告
```

### 测试

```bash
# 后端测试（pytest）
cd knowledge-process-api
uv run pytest tests/ -v

# 前端测试（vitest）
cd apps/knowledge-process-demo
pnpm test
```

### 部署

#### 前端部署到 GitHub Pages

推送到 `main` 分支后，GitHub Actions 自动构建部署。

需要配置的环境变量：
- `VITE_API_BASE`: 后端 API 地址

#### 后端部署到 Hugging Face Spaces

```bash
hf upload spaces/RodeyManager/knowledge-process-api knowledge-process-api/ \
  --exclude ".venv" \
  --exclude "__pycache__" \
  --exclude "*.pyc" \
  --exclude "uv.lock" \
  --commit-message "部署描述"
```

---

## 命名约定与规范

### Git 提交规范

使用 Conventional Commits 格式：

| 类型 | 说明 |
|------|------|
| `feat:` | 新功能 |
| `fix:` | 修复 bug |
| `chore:` | 构建/工具变更 |
| `docs:` | 文档更新 |
| `ci:` | CI/CD 变更 |

### Python 代码规范

- 使用类型提示（type hints）
- 使用 dataclass 定义数据模型
- 遵循 PEP 8 规范
- 注释使用中文

### Vue 代码规范

- 使用 Vue 3 Composition API
- 组件命名使用 PascalCase
- 样式使用 scoped CSS

---

## 环境变量

### 后端环境变量

| 变量名 | 必填 | 说明 | 默认值 |
|--------|------|------|--------|
| `MINERU_API_URL` | 否 | MinerU API 地址 | - |
| `MINERU_API_KEY` | 否 | MinerU API 密钥 | - |

### 前端环境变量

| 变量名 | 说明 |
|--------|------|
| `VITE_API_BASE` | 后端 API 基础地址 |

---

## License

MIT License
