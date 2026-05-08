---
name: multi-strategy-chunking
overview: 在现有项目中扩展多种文本分块策略（固定长度、滑动窗口、递归字符、基于结构、语义分块），统一后端接口标准并增强前端交互展示与算法切换机制。
design:
  styleKeywords:
    - Cyberpunk Neon
    - Dark Mode
    - Glassmorphism
    - Tech Dashboard
    - Responsive
  fontSystem:
    fontFamily: Noto Sans SC
    heading:
      size: 1.4rem
      weight: 600
    subheading:
      size: 1rem
      weight: 500
    body:
      size: 0.85rem
      weight: 400
  colorSystem:
    primary:
      - "#06b6d4"
      - "#00ff88"
      - "#6366f1"
    background:
      - "#0a0e1a"
      - "#0f1525"
      - "#141b2d"
    text:
      - "#e2e8f0"
      - "#94a3b8"
      - "#64748b"
    functional:
      - "#ef4444"
      - "#f59e0b"
      - "#a78bfa"
todos:
  - id: backend-strategies
    content: 重构后端 chunkers 模块：提取递归策略并新建固定长度、滑动窗口、结构、语义四种策略类
    status: completed
  - id: backend-api
    content: 扩展 FastAPI /api/chunk 接口，接入 ChunkRegistry 策略工厂
    status: completed
    dependencies:
      - backend-strategies
  - id: frontend-composable
    content: 开发 useChunking composable，实现分块状态管理与多策略 API 调用
    status: completed
  - id: frontend-components
    content: 使用 [skill:frontend-design] 实现 ChunkParamsPanel 与 ChunkResultPanel 组件
    status: completed
    dependencies:
      - frontend-composable
  - id: frontend-integration
    content: 改造 KnowledgeProcessDemo.vue Step 3，集成算法切换、动态参数与对比视图
    status: completed
    dependencies:
      - backend-api
      - frontend-components
  - id: validation
    content: 更新 pyproject.toml 依赖，验证五种策略端到端运行与前端渲染
    status: completed
    dependencies:
      - frontend-integration
---

## 产品概述

在当前知识库文档处理 Demo 的基础上，扩展文本分块模块，支持五种主流分块策略的灵活切换与对比展示。

## 核心功能

- **后端算法扩展**：在现有递归分块基础上，补足固定长度分块、滑动窗口分块、基于结构的分块（Markdown/HTML 标题层级）及语义分块（TF-IDF 余弦相似度）。
- **统一策略接口**：采用策略模式重构 chunkers 模块，所有算法实现统一的 `ChunkStrategy` 接口，并通过注册表/工厂对外暴露。
- **API 兼容与扩展**：扩展 `POST /api/chunk` 接口，增加 `strategy` 字段用于算法切换，保留现有参数默认值确保向后兼容。
- **前端动态交互**：Step 3「文本分块」页面增加算法选择器，根据所选算法动态渲染专属参数面板。
- **结果对比视图**：支持单算法结果查看与多算法并行对比两种模式，分块结果以卡片列表呈现，展示每块序号、字符数、前后重叠标识。
- **状态管理**：将分块相关的状态、API 调用、缓存逻辑抽离为 `useChunking` composable，保持页面组件简洁。

## Tech Stack

- **后端**：Python 3.10 + FastAPI + Pydantic
- **前端**：Vue 3 (Composition API) + Vite + 原生 CSS（无第三方 UI 库）
- **新增依赖**：`scikit-learn`（TF-IDF 语义分块）

## Implementation Approach

### 后端策略模式重构

将现有 `text_chunker.py` 中的单体式递归逻辑拆解为策略家族：

1. 定义抽象基类 `ChunkStrategy`，约束 `split(text: str, **kwargs) -> SplitResponse` 接口。
2. 将现有 `common_split` / `markdown_table_split` 封装为 `RecursiveChunkStrategy`。
3. 新增 `FixedChunkStrategy`（固定长度硬切）、`SlidingWindowChunkStrategy`（滑动窗口，步长 `chunk_size - overlap`）、`StructureChunkStrategy`（Markdown `#` 标题或 HTML `h1-h6/div` 标签切分，保留标题上下文）、`SemanticChunkStrategy`（句子级 TF-IDF 向量 + 余弦相似度，在相似度低于阈值处切分）。
4. 提供 `ChunkRegistry` 工厂，根据字符串 key 返回策略实例。

### 统一接口设计

扩展 `ChunkRequest` 平铺所有可能参数（各策略按需取用），前端无需根据策略改变请求体结构：

```python
class ChunkRequest(BaseModel):
    text: str
    strategy: str = "recursive"          # fixed | sliding_window | recursive | structure | semantic
    chunk_size: int = 500
    overlap_ratio: float = 0.2
    paragraph_chunk_deep: int = 2
    semantic_threshold: float = 0.5      # 语义分块专用
    structure_type: str = "markdown"     # structure 专用：markdown | html
```

### 语义分块实现细节

- 使用 `sklearn.feature_extraction.text.TfidfVectorizer` 将句子转为向量。
- 计算相邻句子余弦相似度，当相似度低于 `semantic_threshold` 时视为话题边界。
- 若环境缺失 scikit-learn， gracefully fallback 到基于词汇重叠率的轻量实现，保证服务可用。

### 前端架构

- **组件拆分**：创建 `ChunkParamsPanel.vue`（动态参数表单）与 `ChunkResultPanel.vue`（结果列表 + 对比视图）。
- **状态抽离**：`useChunking.js` 集中管理 `strategy`、`params`、`results`、加载态与错误态。
- **对比模式**：前端对选中的多个策略依次调用 `/api/chunk`，结果聚合到 `results` Map 中，结果面板以 Tab 形式切换。

### 性能考量

- 语义分块的 TF-IDF 计算在短文本（Demo 场景）下耗时可忽略；若输入超长，先按段落粗分再在各段内做语义细拆，避免全量矩阵过大。
- 对比模式采用 `Promise.all` 并行请求，减少用户等待时间。

## Implementation Notes

- **Grounded**：保留 `text_chunker.py` 中现有 `split_text_2_chunks` 函数签名作为兼容层，内部委托给 `RecursiveChunkStrategy`，避免破坏已有调用方。
- **Blast radius**：`app.py` 中除 `ChunkRequest`/`ChunkResponse` 外，其他路由与模型不受影响；前端仅改造 Step 3 区域，其余步骤维持原状。
- **Logging**：后端复用现有异常处理模式（`try/except` 转 `HTTPException`），不在循环中打印单块日志，防止日志膨胀。
- **中文注释**：所有新增代码文件与注释必须使用中文。

## Architecture Design

```
knowledge-process-api/
├── app.py                              # [MODIFY] 扩展 ChunkRequest/Response，路由调用注册表
├── src/fastgpt_demo/chunkers/
│   ├── __init__.py                     # [MODIFY] 暴露 ChunkRegistry 与策略常量
│   ├── base.py                         # [NEW] ChunkStrategy ABC + SplitResponse 类型
│   ├── registry.py                     # [NEW] 策略注册表/工厂
│   ├── text_chunker.py                 # [MODIFY] 兼容层：split_text_2_chunks 委托 RecursiveChunkStrategy
│   ├── recursive_chunker.py            # [NEW] 从 text_chunker.py 提取的递归分块策略
│   ├── fixed_chunker.py                # [NEW] 固定长度分块
│   ├── sliding_window_chunker.py       # [NEW] 滑动窗口分块
│   ├── structure_chunker.py            # [NEW] Markdown/HTML 结构分块
│   └── semantic_chunker.py             # [NEW] TF-IDF 语义分块（含 sklearn 不可用时的 fallback）
```

## Directory Structure

### 后端变更

- `knowledge-process-api/pyproject.toml` **[MODIFY]**：在 `dependencies` 追加 `scikit-learn>=1.4.0`。
- `knowledge-process-api/app.py` **[MODIFY]**：
- 扩展 `ChunkRequest` 模型，增加 `strategy` 等字段。
- `chunk` 路由改为通过 `ChunkRegistry` 获取策略实例并执行。
- `knowledge-process-api/src/fastgpt_demo/chunkers/__init__.py` **[MODIFY]**：导出 `ChunkRegistry`、策略常量、`split_text_2_chunks`（兼容层）。
- `knowledge-process-api/src/fastgpt_demo/chunkers/text_chunker.py` **[MODIFY]**：保留 `split_text_2_chunks` 函数，内部实例化 `RecursiveChunkStrategy` 并转发参数；原有 `common_split` 等逻辑迁移至 `recursive_chunker.py`。
- `knowledge-process-api/src/fastgpt_demo/chunkers/base.py` **[NEW]**：定义 `SplitResponse` TypedDict 与 `ChunkStrategy` 抽象基类。
- `knowledge-process-api/src/fastgpt_demo/chunkers/registry.py` **[NEW]**：`ChunkRegistry` 字典映射，提供 `get_strategy(name: str) -> ChunkStrategy`。
- `knowledge-process-api/src/fastgpt_demo/chunkers/recursive_chunker.py` **[NEW]**：从原 `text_chunker.py` 迁移的递归分块策略类，包含 `common_split`、`markdown_table_split` 及全部辅助函数。
- `knowledge-process-api/src/fastgpt_demo/chunkers/fixed_chunker.py` **[NEW]**：`FixedChunkStrategy`，按固定字符数切分，最后不足长度直接保留。
- `knowledge-process-api/src/fastgpt_demo/chunkers/sliding_window_chunker.py` **[NEW]**：`SlidingWindowChunkStrategy`，窗口大小 `chunk_size`，步长 `chunk_size - overlap_len`，支持首尾去重。
- `knowledge-process-api/src/fastgpt_demo/chunkers/structure_chunker.py` **[NEW]**：`StructureChunkStrategy`，支持 `structure_type="markdown"`（按 `#` 层级）与 `"html"`（按 `h1-h6` / `section` / `article` 标签），块头保留层级标题作为上下文。
- `knowledge-process-api/src/fastgpt_demo/chunkers/semantic_chunker.py` **[NEW]**：`SemanticChunkStrategy`，先按句子拆分，计算相邻句 TF-IDF 余弦相似度，低于阈值则切分；若 `sklearn` 未安装则回退到基于词汇重叠率的轻量实现。

### 前端变更

- `apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue` **[MODIFY]**：
- Step 3 区域替换为使用 `ChunkParamsPanel` 与 `ChunkResultPanel`。
- 引入 `useChunking` 管理分块状态与 API 调用。
- 统计栏增加「当前算法」与「耗时」指标。
- `apps/knowledge-process-demo/src/composables/useChunking.js` **[NEW]**：
- 维护 `strategy`、`params`、`results`、`loading`、`error`。
- 提供 `runChunk(strategy)` 与 `runCompare(strategies[])` 方法。
- 对不同策略缓存结果，避免重复请求。
- `apps/knowledge-process-demo/src/components/ChunkParamsPanel.vue` **[NEW]**：
- 接收 `strategy` 与 `params` 的 v-model。
- 根据 `strategy` 动态渲染不同参数控件（滑块、下拉框、数值输入）。
- `apps/knowledge-process-demo/src/components/ChunkResultPanel.vue` **[NEW]**：
- 支持「单结果」与「对比」两种模式。
- 单结果：卡片列表展示每个 chunk，标注序号、字符数、与下一块的重叠文本长度。
- 对比：侧边 Tab 切换不同算法结果，顶部展示各算法分块数量、平均块大小、总字符数对比表。

## Key Code Structures

```python
# base.py
from abc import ABC, abstractmethod
from typing import Dict, List

SplitResponse = Dict[str, object]  # {"chunks": List[str], "chars": int}

class ChunkStrategy(ABC):
    @abstractmethod
    def split(self, text: str, **kwargs) -> SplitResponse:
        """执行分块并返回结果，所有子类必须实现"""
        ...
```

```python
# registry.py
from .recursive_chunker import RecursiveChunkStrategy
from .fixed_chunker import FixedChunkStrategy
from .sliding_window_chunker import SlidingWindowChunkStrategy
from .structure_chunker import StructureChunkStrategy
from .semantic_chunker import SemanticChunkStrategy

_STRATEGIES = {
    "recursive": RecursiveChunkStrategy,
    "fixed": FixedChunkStrategy,
    "sliding_window": SlidingWindowChunkStrategy,
    "structure": StructureChunkStrategy,
    "semantic": SemanticChunkStrategy,
}

class ChunkRegistry:
    @staticmethod
    def get(name: str) -> ChunkStrategy:
        ...
```

```python
# app.py 扩展模型
class ChunkRequest(BaseModel):
    text: str
    strategy: str = "recursive"
    chunk_size: int = 500
    overlap_ratio: float = 0.2
    paragraph_chunk_deep: int = 2
    semantic_threshold: float = 0.5
    structure_type: str = "markdown"
```

## 设计风格

延续项目现有的暗色科技风（Cyberpunk Neon），以深蓝黑为底色、青色与绿色为强调色，保持界面的一致性与沉浸感。新增的分块交互区域采用玻璃拟态卡片（Glassmorphism）与微光边框，突出算法切换与结果对比的科技感。

## 页面架构（Step 3 文本分块）

### 顶部控制栏

- 算法选择器：下拉菜单切换五种分块策略，当前选中项高亮显示。
- 模式切换按钮：「单算法运行」/「多算法对比」，对比模式下可多选策略。

### 左侧参数面板（动态渲染）

- 公共参数：块大小滑块（100-8000）、重叠率滑块（0%-40%）。
- 策略专属参数：
- 递归分块：段落深度滑块（1-5）。
- 结构分块：结构类型单选（Markdown / HTML）。
- 语义分块：相似度阈值滑块（0.1-0.9）。
- 操作按钮：「执行分块」（渐变青色按钮）、「重置参数」。

### 右侧结果面板

- 单结果模式：
- 顶部统计条：分块数量、平均大小、总字符数、处理耗时。
- Chunk 卡片流：每张卡片顶部显示「Chunk #N · 1234 字符 · 与下块重叠 56 字符」，正文以等宽字体展示，支持展开/收起。
- 对比模式：
- 顶部横向对比表：各算法的分块数、平均大小、最大/最小块。
- 下方 Tab 栏切换不同算法，每个 Tab 内展示该算法的 Chunk 卡片流。
- 采用分栏布局（桌面端）或垂直堆叠（移动端），确保对比直观。

## 响应式与交互

- 桌面端：左右分栏（结果区 : 参数区 = 1 : 320px）。
- 移动端（< 768px）：参数面板折叠为顶部可展开区域，结果区全宽。
- 微动画：卡片 hover 时边框泛青色微光，参数切换时面板高度平滑过渡，加载时分块按钮显示旋转动效。

## Agent Extensions

### Skill

- **frontend-design**
- Purpose: 为 ChunkParamsPanel 与 ChunkResultPanel 设计并生成高质量、风格统一的 Vue 组件代码，确保暗色科技风的视觉一致性与微交互动效。
- Expected outcome: 产出可直接使用的 Vue SFC 组件，包含动态参数渲染、结果卡片列表、对比视图及响应式布局。

### SubAgent

- **code-explorer**
- Purpose: 在重构后端 chunkers 模块时，协助检索项目中所有引用 `split_text_2_chunks` 或 `common_split` 的代码位置，确保迁移无遗漏。
- Expected outcome: 提供完整的引用清单，验证重构后无残留旧调用或符号断裂。