# fastgpt-report

FastGPT 源码分析报告与文档处理流水线 Demo。

## 项目结构

```
fastgpt-report/
├── apps/fastgpt-report/    # Vue 分析报告 Web 应用
├── demo/                   # Python Streamlit Demo（复刻文档处理流水线）
└── packages/               # 共享包（预留）
```

## Vue 分析报告

基于 Vue 3 + Vite + ECharts 的 FastGPT 源码分析报告，涵盖 14 个章节：

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
14. 文档处理 Demo

已部署至 GitHub Pages：`https://rodeymanager.github.io/fastgpt-report/`

### 开发

```bash
pnpm install
pnpm dev
```

### 构建

```bash
pnpm build
```

## Python Demo

`demo/` 目录包含一个独立的 Python 项目，使用 Streamlit 交互式复刻 FastGPT 的 5 步文档处理流水线：

| 步骤 | 功能 | Python 库 | 对应 FastGPT 模块 |
|------|------|-----------|-------------------|
| 1. 文档解析 | PDF / DOCX / CSV / XLSX / PPTX / TXT | PyMuPDF, mammoth, openpyxl, python-pptx, chardet | `core/dataset/*/readFileFn` |
| 2. Markdown 转换 | HTML → Markdown | markdownify, beautifulsoup4 | `turndownService` |
| 3. 数据清洗 | 中文空格 / 换行 / 控制字符 | — | `simpleText`, `fastGPTSimpleText` |
| 4. 文本分块 | 递归多策略分块 | — | `commonSplit`, `splitTextRecursively` |
| 5. 图片索引 | 图片预览 + VLM 描述 | Pillow | `ImageIndexer` |

分块算法完全复刻 FastGPT 的 `commonSplit` + `splitTextRecursively` 递归多级分块逻辑。

### 环境要求

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

### 运行

```bash
cd demo
uv sync
uv run streamlit run app.py
```

浏览器打开 `http://localhost:8501`。

## 技术栈

| 组件 | 技术 |
|------|------|
| 分析报告 | Vue 3, Vite, ECharts, vue-echarts, vue-router |
| 文档解析 (JS) | pdfjs-dist, mammoth, xlsx (SheetJS), papaparse, turndown |
| 文档解析 (Python) | PyMuPDF, mammoth, openpyxl, python-pptx, markdownify, chardet, Pillow |
| 交互式 Demo | Streamlit |
| 包管理 | pnpm (monorepo), uv (Python) |
| 部署 | GitHub Pages + GitHub Actions |

## License

MIT
