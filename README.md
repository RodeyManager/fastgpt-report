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

### 前端：apps/knowledge-process-demo

Vue 3 + Vite 交互式 Demo，提供文档处理 5 步流水线的可视化操作界面，所有处理逻辑通过 API 调用后端完成。

### 后端：knowledge-process-api

Python FastAPI REST API，提供文档解析、Markdown 转换、数据清洗、文本分块、图片索引的 REST 接口。

| 端点 | 功能 |
|------|------|
| `POST /api/parse` | 文档解析（PDF/DOCX/CSV/XLSX/PPTX/TXT） |
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

### 前端技术

- Vue 3 + Vite + vue-router（与 fastgpt-report 一致）
- 所有文档处理通过 FastAPI 后端完成，前端仅负责 UI 展示

## 技术栈

| 组件 | 技术 |
|------|------|
| 分析报告 | Vue 3, Vite, ECharts, vue-echarts, vue-router |
| Demo 前端 | Vue 3, Vite, vue-router |
| Demo 后端 | FastAPI, uvicorn, PyMuPDF, mammoth, openpyxl, python-pptx, markdownify, chardet, Pillow |
| 包管理 | pnpm (monorepo), uv (Python) |
| 部署 | GitHub Pages + GitHub Actions |

## License

MIT
