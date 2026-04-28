# fastgpt-report

FastGPT 源码分析报告与文档处理流水线 Demo。

## 项目结构

```
fastgpt-report/
├── apps/fastgpt-report/          # Vue 分析报告 Web 应用（13 章节）
├── apps/knowledge-process-demo/  # Vue 文档处理 Demo 前端（5 步流水线）
├── knowledge-process-api/        # Python FastAPI 后端（文档处理 REST API）
└── packages/                     # 共享包（预留）
```

## Vue 分析报告

基于 Vue 3 + Vite + ECharts 的 FastGPT 源码分析报告，涵盖 13 个章节：

1. 项目概览
2. 架构设计
3. 文档上传与解析
4. 数据清洗
5. 文本分块
6. 图片索引与 VLM
7. 向量嵌入
8. 检索与召回
9. 训练与微调
10. 总结与展望
11. 数据库 Schema
12. 依赖关系分析
13. 架构细节

已部署至 GitHub Pages：
- 分析报告：`https://rodeymanager.github.io/fastgpt-report/`
- 文档处理 Demo：`https://rodeymanager.github.io/fastgpt-report/demo/`

### 开发

```bash
pnpm install
pnpm dev
```

### 构建

```bash
pnpm build
```

## 文档处理 Demo（前后端分离）

交互式文档处理流水线 Demo，完整复刻 FastGPT 知识库的文档处理链路。支持多工具解析对比，可直观比较不同解析引擎的效果差异。

在线体验：`https://rodeymanager.github.io/fastgpt-report/demo/`

### 五步流水线

| 步骤 | 功能 | 说明 |
|------|------|------|
| Step 0 | 文档解析 | 上传文件，选择解析引擎，提取文本/HTML/表格 |
| Step 1 | Markdown 转换 | 将解析结果转为 Markdown（DOCX→MD、表格→MD 等） |
| Step 2 | 数据清洗 | 去空白、规范化换行、移除中文字符间空格等 |
| Step 3 | 文本分块 | 递归多级分块，支持自定义块大小和重叠率 |
| Step 4 | 图片索引 | 提取文档图片并生成描述（需 VLM 模型） |

### 多工具解析对比

解析步骤支持选择不同解析引擎，可左右并排对比同一文件在不同工具下的解析效果：

| 引擎 | 支持格式 | 说明 |
|------|----------|------|
| FastGPT 默认 | PDF, DOCX, CSV, XLSX, PPTX, TXT, 图片 | 项目内置解析器，与 FastGPT 后端一一对应 |
| MinerU | PDF, DOCX, PPTX, 图片 | 高质量解析（表格识别、公式提取、版面还原），当前为 Placeholder 模式 |

使用方式：上传文件后，在「解析选项」区域选择引擎，分别点击「开始解析」，两个引擎的结果会同时保留并排展示。

### 前端：apps/knowledge-process-demo

Vue 3 + Vite 单页应用，提供可视化操作界面，所有处理逻辑通过 API 调用后端完成。

### 后端：knowledge-process-api

Python FastAPI REST API，提供文档解析、Markdown 转换、数据清洗、文本分块、图片索引的 REST 接口。

| 端点 | 功能 |
|------|------|
| `POST /api/parse` | 文档解析，支持 `engine` 参数选择引擎（默认 `fastgpt`） |
| `POST /api/convert` | Markdown 转换 |
| `POST /api/clean` | 数据清洗 |
| `POST /api/chunk` | 文本分块 |
| `POST /api/index-image` | 图片索引 |
| `GET /api/health` | 健康检查 |

Python 解析库与 FastGPT 后端一一对应：

| 文件类型 | Python 库 | 对应 FastGPT 模块 |
|----------|-----------|-------------------|
| PDF | PyMuPDF | `readFileFn/pdf.ts` |
| DOCX | mammoth | `readFileFn/docx.ts` |
| CSV/XLSX | openpyxl | `readFileFn/csv.ts`, `readFileFn/xlsx.ts` |
| PPTX | python-pptx | `readFileFn/pptx.ts` |
| TXT | chardet (编码检测) | `readFileFn/text.ts` |
| HTML→MD | markdownify, beautifulsoup4 | `turndownService` |

分块算法完全复刻 FastGPT 的 `commonSplit` + `splitTextRecursively` 递归多级分块逻辑。

### 本地运行

```bash
# 1. 启动后端
cd knowledge-process-api
uv sync
uv run uvicorn app:app --reload --port 8000

# 2. 启动前端（新终端）
cd apps/knowledge-process-demo
pnpm dev
# 浏览器打开 http://localhost:3001
```

### 测试

```bash
# 后端测试（pytest）
cd knowledge-process-api
uv run pytest tests/ -v          # 11 tests

# 前端测试（vitest）
cd apps/knowledge-process-demo
pnpm test                        # 9 tests
```

### 部署

前端部署到 GitHub Pages，后端部署到 Hugging Face Spaces。

**后端（Hugging Face Spaces）：**

使用 `hf upload` CLI 推送（详见 [AGENTS.md](./AGENTS.md)）：

```bash
# 从项目根目录执行
hf upload spaces/RodeyManager/knowledge-process-api knowledge-process-api/ \
  --exclude ".venv" \
  --exclude "__pycache__" \
  --exclude "*.pyc" \
  --exclude "uv.lock" \
  --commit-message "描述信息"
```

部署地址：`https://rodeymanager-knowledge-process-api.hf.space`

**前端（GitHub Pages）：**
1. 在 GitHub 仓库 **Settings** → **Secrets and variables** → **Actions** → **Variables** 中添加：
   - `VITE_API_BASE` = `https://rodeymanager-knowledge-process-api.hf.space`
2. 推送代码到 `main`，GitHub Actions 自动构建部署

## 技术栈

| 组件 | 技术 |
|------|------|
| 分析报告 | Vue 3, Vite, ECharts, vue-echarts, vue-router |
| Demo 前端 | Vue 3, Vite, vue-router, vitest, @vue/test-utils |
| Demo 后端 | FastAPI, uvicorn, PyMuPDF, mammoth, openpyxl, python-pptx, markdownify, chardet, Pillow, httpx |
| 测试 | pytest (后端), vitest (前端) |
| 包管理 | pnpm (monorepo), uv (Python) |
| 部署 | GitHub Pages (前端) + Hugging Face Spaces (后端) + GitHub Actions |

## License

MIT
