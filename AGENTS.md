# Project Conventions

## Project Structure

- `apps/fastgpt-report/` — Vue 3 分析报告（13 章节）
- `apps/knowledge-process-demo/` — Vue 3 文档处理 Demo 前端
- `knowledge-process-api/` — Python FastAPI 后端（文档处理 REST API）

## Deployment Targets

| Component           | Target              | URL                                                                |
| ------------------- | ------------------- | ------------------------------------------------------------------ |
| 前端（报告 + Demo） | GitHub Pages        | `https://rodeymanager.github.io/fastgpt-report/`                   |
| 后端 API            | Hugging Face Spaces | `https://huggingface.co/spaces/RodeyManager/knowledge-process-api` |

## Hugging Face Spaces 部署规范

### 上传命令

```bash
# 从项目根目录执行，必须排除 .venv / __pycache__ / uv.lock
hf upload spaces/RodeyManager/knowledge-process-api knowledge-process-api/ \
  --exclude ".venv" \
  --exclude "__pycache__" \
  --exclude "*.pyc" \
  --exclude "uv.lock" \
  --commit-message "描述信息"
```

### 必须排除的文件

| 目录/文件      | 原因                                                |
| -------------- | --------------------------------------------------- |
| `.venv/`       | Python 虚拟环境，Docker 构建时由 `uv sync` 重新生成 |
| `__pycache__/` | 编译缓存                                            |
| `*.pyc`        | 字节码缓存                                          |
| `uv.lock`      | 锁文件，HF 构建时会重新生成                         |

> ⚠️ `hf upload` **不会**自动读取 `.gitignore`，必须通过 `--exclude` 显式排除。

## API 接口规范

### POST /api/parse

`method` 参数仅接受以下值：

| 值     | 说明                                 |
| ------ | ------------------------------------ |
| `auto` | 根据文件扩展名自动选择解析器（推荐） |
| `pdf`  | PDF 解析（PyMuPDF）                  |
| `docx` | DOCX 解析（mammoth）                 |
| `csv`  | CSV 解析                             |
| `xlsx` | XLSX 解析（openpyxl）                |
| `pptx` | PPTX 解析（python-pptx）             |
| `text` | 纯文本解析（chardet 编码检测）       |
| `html` | HTML 解析（BeautifulSoup4）           |

前端 `parseMethod` 仅用于控制 UI 展示（HTML 预览 vs 纯文本），**API 调用统一使用 `method=auto`**。

## Git 规范

- Commit message 使用 Conventional Commits 格式：`feat:`, `fix:`, `chore:`, `docs:`, `ci:`
- 前端改动推送到 `main` 分支后，GitHub Actions 自动构建部署到 GitHub Pages

## 必须遵循的规则

- 必须使用中文回答；
- 代码注释必须使用中文；
