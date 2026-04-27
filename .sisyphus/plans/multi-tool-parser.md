# 多工具文档解析对比功能

## TL;DR

> **Quick Summary**: 在现有文档处理 Demo 中添加解析工具选择器（FastGPT 默认 / MinerU），支持左右并排对比同一文件在不同工具下的解析效果，选中工具的结果影响下游流水线。
> 
> **Deliverables**:
> - 后端：`engine` 参数支持 + MinerU API 客户端（placeholder 模式）
> - 前端：工具选择器 UI + 左右并排结果对比视图
> - 测试：pytest + vitest 基础设施 + TDD 测试用例
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Task 0 (test infra) → Task 1 (backend engine) → Task 3 (frontend selector) → Task 4 (comparison UI) → F1-F4

---

## Context

### Original Request
用户希望在文档解析步骤中，能选择不同的解析工具（如 FastGPT 默认、MinerU 等），直观对比各工具的解析效果。默认使用 FastGPT 方法，MinerU 处理 PDF/DOCX/PPTX/图片，其他文件类型保留现有解析器。

### Interview Summary
**Key Discussions**:
- **工具范围**: FastGPT 默认 + MinerU，先做两个，后续可扩展
- **对比 UX**: 左右并排对比，选择工具后单独解析
- **MinerU 集成**: API 服务方式，先预留接口配置后续填入
- **下游影响**: 选中工具的解析结果影响整个流水线（MD转换/清洗/分块）
- **文件类型**: 前端只传文件，后端根据类型自动路由
- **测试策略**: TDD 模式（需要先建立测试基础设施）

**Research Findings**:
- 前端：单文件组件 `KnowledgeProcessDemo.vue`（1074行），无子组件/composables
- 后端：`parsers/__init__.py` 平铺调度字典，无引擎抽象层
- API：`/api/parse` 仅接受 `file` + `method`（文件类型），无 `engine` 参数
- `parseMethod` 仅控制 UI 展示，始终发 `method: 'auto'` 到 API
- 项目无测试框架

### Metis Review
**Identified Gaps** (addressed):
- MinerU 不可用时的错误处理 → 显示错误面板，不阻塞 UI
- 不支持的文件类型 + MinerU → 后端 422 + 前端禁用/警告
- 两个工具结果需同时保留在状态中 → `Map<engine, ParseResult>`
- 无测试框架是 TDD 的阻塞前提 → Task 0 单独处理

---

## Work Objectives

### Core Objective
为文档解析 Demo 添加多工具解析对比功能，让用户可以选择 FastGPT 默认或 MinerU 解析同一文件，左右并排查看解析结果差异，选中工具的结果贯穿下游流水线。

### Concrete Deliverables
- `knowledge-process-api/src/fastgpt_demo/parsers/mineru_parser.py` — MinerU API 客户端（placeholder 模式）
- `knowledge-process-api/app.py` — `/api/parse` 增加 `engine` 参数
- `knowledge-process-api/tests/` — pytest 测试基础设施 + 测试用例
- `apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue` — 工具选择器 + 对比视图
- `apps/knowledge-process-demo/tests/` — vitest 测试基础设施 + 测试用例

### Definition of Done
- [ ] `curl -F "file=@test.pdf" -F "engine=fastgpt" localhost:8000/api/parse` → 正常返回 ParseResult
- [ ] `curl -F "file=@test.pdf" -F "engine=mineru" localhost:8000/api/parse` → 返回 placeholder ParseResult
- [ ] `curl -F "file=@test.pdf" localhost:8000/api/parse`（无 engine）→ 与当前行为完全一致
- [ ] `curl -F "file=@test.csv" -F "engine=mineru" localhost:8000/api/parse` → 返回 422 错误
- [ ] 前端工具选择器显示 2 个选项："FastGPT 默认" 和 "MinerU"
- [ ] 两个工具的解析结果同时保留，可切换查看对比
- [ ] 选中工具的结果正确流经下游流水线
- [ ] `pytest` 全部通过
- [ ] `vitest` 全部通过

### Must Have
- 后端 `engine` 参数默认 `'fastgpt'`，向后兼容
- MinerU placeholder 返回合理的模拟数据（非空字符串）
- 前端存储两个工具的结果直到文件变更或页面刷新
- 不支持的文件类型 + MinerU → 后端 422 + 前端禁用选择器
- MinerU 不可用/超时时显示错误信息，不阻塞 UI
- 用户切换文件时清除两个工具的结果

### Must NOT Have (Guardrails)
- ❌ 不重构 1074 行 SFC 为子组件（在现有结构内工作）
- ❌ 不构建通用引擎抽象/注册表/插件系统（简单的 if/else 或字典调度即可）
- ❌ 不实现结果 diff 高亮或质量评分
- ❌ 不添加 localStorage 缓存或对比历史
- ❌ 不自动批量运行两个工具（用户选择后单独解析）
- ❌ 不添加解析耗时显示（V1 不做）
- ❌ 不修改现有 ParseResult 字段（只扩展）
- ❌ 不做 E2E 测试（仅单元测试 + 组件测试）

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO（需要建立）
- **Automated tests**: TDD（先写测试后实现）
- **Framework**: pytest (后端) + vitest (前端)
- **TDD workflow**: RED (failing test) → GREEN (minimal impl) → REFACTOR

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Backend**: Use Bash (curl) — Send requests, assert status + response fields
- **Frontend**: Use Bash (vitest) — Run component tests, assert rendering + state
- **Integration**: Use Bash (curl + frontend dev server) — Full flow verification

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - test infrastructure + backend engine):
├── Task 0: 建立 pytest 测试基础设施 [quick]
├── Task 1: 后端 — 添加 engine 参数 + MinerU placeholder 客户端 [deep]
└── Task 2: 前端 — 建立 vitest 测试基础设施 [quick]

Wave 2 (After Wave 1 - tests + frontend):
├── Task 3: 后端测试 — TDD: engine 调度 + MinerU 客户端 + 错误处理 [unspecified-high]
├── Task 4: 前端 — 工具选择器 UI + 多引擎状态管理 [visual-engineering]
└── Task 5: 前端 — 左右并排结果对比视图 [visual-engineering]

Wave 3 (After Wave 2 - integration + frontend tests):
├── Task 6: 前端测试 — TDD: 工具选择器 + 对比视图 [unspecified-high]
└── Task 7: 集成验证 — 全流程测试 (curl + 前端) [deep]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 0 → Task 1 → Task 3 → Task 4 → Task 5 → Task 7 → F1-F4
Parallel Speedup: ~50% faster than sequential
Max Concurrent: 3 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 0 | - | 3 |
| 1 | - | 3, 4 |
| 2 | - | 6 |
| 3 | 0, 1 | 7 |
| 4 | 1 | 5, 7 |
| 5 | 4 | 6, 7 |
| 6 | 2, 5 | 7 |
| 7 | 3, 4, 5, 6 | F1-F4 |

### Agent Dispatch Summary

- **Wave 1**: 3 tasks — T0 → `quick`, T1 → `deep`, T2 → `quick`
- **Wave 2**: 3 tasks — T3 → `unspecified-high`, T4 → `visual-engineering`, T5 → `visual-engineering`
- **Wave 3**: 2 tasks — T6 → `unspecified-high`, T7 → `deep`
- **FINAL**: 4 tasks — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

> Implementation + Test = ONE Task. Never separate.
> EVERY task MUST have: Recommended Agent Profile + Parallelization info + QA Scenarios.

- [ ] 0. 建立 pytest 测试基础设施

  **What to do**:
  - 在 `knowledge-process-api/` 创建 `pytest.ini` 配置文件（testpaths, python_files 等）
  - 创建 `tests/conftest.py` — 共享 fixtures（test client, sample PDF buffer, sample CSV buffer）
  - 创建 `tests/__init__.py`
  - 在 `pyproject.toml` 中添加 pytest 依赖到 `[project.optional-dependencies]` 或 dev 依赖
  - 创建一个冒烟测试 `tests/test_health.py`：验证 `/api/health` 返回 `{"status": "ok"}`
  - 运行 `pytest tests/ -v` 确保通过

  **Must NOT do**:
  - 不修改任何现有源代码
  - 不添加任何业务逻辑测试（仅基础设施）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 纯配置文件创建，无复杂逻辑
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `hf-cli`: 不涉及 HF 部署

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Task 3
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to follow):
  - `knowledge-process-api/app.py:122-124` — `/api/health` 端点，冒烟测试的目标
  - `knowledge-process-api/pyproject.toml` — 现有依赖和项目配置格式

  **External References**:
  - pytest 配置: `https://docs.pytest.org/en/stable/reference/customize.html`

  **WHY Each Reference Matters**:
  - `app.py:122-124` — 需要知道 FastAPI test client 如何创建（from fastapi.testclient import TestClient）
  - `pyproject.toml` — 需要匹配现有依赖格式添加 pytest

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: pytest infrastructure works
    Tool: Bash
    Preconditions: knowledge-process-api 目录存在，venv 已激活
    Steps:
      1. cd knowledge-process-api && uv add --dev pytest httpx
      2. pytest tests/test_health.py -v
      3. Assert output contains "1 passed"
    Expected Result: pytest 成功运行，冒烟测试通过
    Failure Indicators: pytest 命令失败，import 错误，test client 创建失败
    Evidence: .sisyphus/evidence/task-0-pytest-infra.txt
  ```

  **Commit**: YES
  - Message: `test(infra): add pytest configuration and fixtures`
  - Files: `knowledge-process-api/pytest.ini`, `knowledge-process-api/tests/conftest.py`, `knowledge-process-api/tests/test_health.py`

- [ ] 1. 后端 — 添加 engine 参数 + MinerU placeholder 客户端

  **What to do**:
  - 在 `app.py` 的 `/api/parse` 端点添加 `engine: str = Form("fastgpt")` 参数
  - 修改 `parsers/__init__.py` 的 `parse_file()` 接受 `engine` 参数，添加引擎级调度逻辑：
    ```python
    # 引擎调度：先按 engine 选解析器组，再按 method 选具体解析函数
    SUPPORTED_MINERU_EXTS = {'.pdf', '.docx', '.doc', '.pptx', '.png', '.jpg', '.jpeg', '.gif', '.webp'}
    
    if engine == "mineru":
        if ext not in SUPPORTED_MINERU_EXTS:
            raise ValueError(f"MinerU does not support {ext} files")
        return parse_mineru(buffer, filename)
    else:  # fastgpt (default)
        # 现有调度逻辑不变
    ```
  - 创建 `parsers/mineru_parser.py`：
    - `parse(buffer, filename) -> ParseResult` 函数
    - 读取环境变量 `MINERU_API_URL` 和 `MINERU_API_KEY`
    - 如果 URL 存在，调用真实 MinerU API（使用 httpx）
    - 如果 URL 不存在，返回 placeholder 模拟数据：
      - `raw_text`: "[MinerU Placeholder] 这是由 MinerU 解析引擎生成的模拟数据。实际使用时将调用 MinerU API 服务。\n\n文件: {filename}\n引擎: MinerU\n\n--- 模拟解析内容 ---\n此文件由 MinerU 文档解析引擎处理。MinerU 支持高质量 PDF/DOCX/PPTX 解析，包括表格识别、公式提取、版面还原等高级功能。"
      - `format_text`: 与 raw_text 相同
      - `html_preview`: `<div style="...">MinerU Placeholder</div>` 包装的 HTML
      - `image_list`: `[]`
      - `sheet_names`: `None`
  - 在 `pyproject.toml` 添加 `httpx` 依赖（用于 MinerU API 调用）
  - 确保无 engine 参数时（默认 `fastgpt`）行为与当前完全一致

  **Must NOT do**:
  - 不修改现有解析器代码
  - 不构建通用引擎注册表/插件系统
  - 不修改现有 ParseResult 字段
  - 不添加超过 2 个引擎选项

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 涉及 API 参数扩展、调度逻辑重构、新客户端模块创建
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `hf-cli`: 不涉及部署

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 0, 2)
  - **Blocks**: Tasks 3, 4
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to follow):
  - `knowledge-process-api/app.py:127-146` — 现有 `/api/parse` 端点，需要在这里添加 `engine` 参数
  - `knowledge-process-api/src/fastgpt_demo/parsers/__init__.py:29-58` — 现有调度逻辑，需要扩展为双层调度
  - `knowledge-process-api/src/fastgpt_demo/parsers/pdf_parser.py` — 参考 parse() 函数签名和返回值

  **API/Type References** (contracts to implement against):
  - `knowledge-process-api/src/fastgpt_demo/parsers/_types.py` — ParseResult 数据类，MinerU 客户端必须返回这个类型

  **External References**:
  - MinerU API 文档（待补充具体 URL）
  - httpx 异步客户端: `https://www.python-httpx.org/async/`

  **WHY Each Reference Matters**:
  - `app.py:127-146` — 理解现有 Form 参数模式，新增 engine 参数需要保持一致
  - `parsers/__init__.py:29-58` — 理解现有调度字典结构，扩展为 engine+method 双层
  - `parsers/_types.py` — MinerU parser 必须返回完全相同的 ParseResult 结构
  - `pdf_parser.py` — 参考现有 parser 的 buffer → ParseResult 转换模式

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Default engine (backward compatibility)
    Tool: Bash (curl)
    Preconditions: 后端服务运行在 localhost:8000
    Steps:
      1. curl -s -F "file=@knowledge-process-api/tests/fixtures/test.pdf" http://localhost:8000/api/parse | python -m json.tool
      2. Assert response has keys: raw_text, format_text, html_preview, image_list
      3. Assert raw_text is not empty
    Expected Result: 与当前 API 行为完全一致，不传 engine 参数时默认 fastgpt
    Failure Indicators: 缺少字段、空结果、HTTP 422
    Evidence: .sisyphus/evidence/task-1-default-engine.json

  Scenario: FastGPT engine explicitly
    Tool: Bash (curl)
    Preconditions: 后端服务运行
    Steps:
      1. curl -s -F "file=@knowledge-process-api/tests/fixtures/test.pdf" -F "engine=fastgpt" http://localhost:8000/api/parse | python -m json.tool
      2. Assert response.raw_text identical to default engine response
    Expected Result: 显式指定 engine=fastgpt 与不传 engine 行为一致
    Failure Indicators: 结果不同、HTTP 错误
    Evidence: .sisyphus/evidence/task-1-fastgpt-engine.json

  Scenario: MinerU engine with PDF (placeholder mode)
    Tool: Bash (curl)
    Preconditions: 后端服务运行，MINERU_API_URL 环境变量未设置
    Steps:
      1. curl -s -F "file=@knowledge-process-api/tests/fixtures/test.pdf" -F "engine=mineru" http://localhost:8000/api/parse | python -m json.tool
      2. Assert response.raw_text contains "MinerU"
      3. Assert response.html_preview is not empty
      4. Assert response has all ParseResult fields
    Expected Result: 返回 placeholder 模拟数据，结构完整
    Failure Indicators: 空字段、缺少字段、HTTP 错误
    Evidence: .sisyphus/evidence/task-1-mineru-placeholder.json

  Scenario: MinerU with unsupported file type (CSV)
    Tool: Bash (curl)
    Preconditions: 后端服务运行
    Steps:
      1. curl -s -w "\nHTTP_CODE:%{http_code}" -F "file=@knowledge-process-api/tests/fixtures/test.csv" -F "engine=mineru" http://localhost:8000/api/parse
      2. Assert HTTP status is 422 or 400
      3. Assert error message mentions unsupported
    Expected Result: 返回 4xx 错误，提示文件类型不支持
    Failure Indicators: HTTP 200、返回了结果
    Evidence: .sisyphus/evidence/task-1-mineru-unsupported.txt
  ```

  **Commit**: YES
  - Message: `feat(api): add engine parameter to /api/parse with MinerU placeholder`
  - Files: `knowledge-process-api/app.py`, `knowledge-process-api/src/fastgpt_demo/parsers/__init__.py`, `knowledge-process-api/src/fastgpt_demo/parsers/mineru_parser.py`

- [ ] 2. 前端 — 建立 vitest 测试基础设施

  **What to do**:
  - 在 `apps/knowledge-process-demo/` 安装 vitest + @vue/test-utils：`pnpm add -D vitest @vue/test-utils @vue/compiler-sfc`
  - 创建 `vitest.config.js`（或修改现有 vite.config.js 添加 test 配置）
  - 创建 `tests/setup.js` — 全局测试 setup
  - 创建冒烟测试 `tests/KnowledgeProcessDemo.test.js`：验证组件能正常 mount
  - 在 `package.json` 添加 `"test": "vitest run"` script
  - 运行 `pnpm test` 确保通过

  **Must NOT do**:
  - 不修改现有组件代码
  - 不添加业务逻辑测试（仅基础设施）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 纯配置文件创建
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 0, 1)
  - **Blocks**: Task 6
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to follow):
  - `apps/knowledge-process-demo/vite.config.js` — 现有 Vite 配置，需要在其中添加 test 配置
  - `apps/knowledge-process-demo/package.json` — 现有依赖和 scripts

  **External References**:
  - vitest Vue 配置: `https://vitest.dev/guide/`
  - @vue/test-utils: `https://test-utils.vuejs.org/`

  **WHY Each Reference Matters**:
  - `vite.config.js` — 需要了解现有配置，决定是在其中添加 test 还是创建独立 vitest.config.js
  - `package.json` — 需要匹配现有 scripts 格式

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: vitest infrastructure works
    Tool: Bash
    Preconditions: apps/knowledge-process-demo 目录存在，node_modules 已安装
    Steps:
      1. cd apps/knowledge-process-demo && pnpm add -D vitest @vue/test-utils
      2. pnpm test
      3. Assert output contains "1 passed" or similar
    Expected Result: vitest 成功运行，冒烟测试通过
    Failure Indicators: vitest 命令失败，import 错误，组件 mount 失败
    Evidence: .sisyphus/evidence/task-2-vitest-infra.txt
  ```

  **Commit**: YES
  - Message: `test(infra): add vitest configuration for frontend`
  - Files: `apps/knowledge-process-demo/vitest.config.js`, `apps/knowledge-process-demo/tests/KnowledgeProcessDemo.test.js`

- [ ] 3. 后端测试 — TDD: engine 调度 + MinerU 客户端 + 错误处理

  **What to do**:
  - TDD RED 阶段 — 先写测试：
    - `tests/test_engine_dispatch.py`:
      - test_default_engine_is_fastgpt：不传 engine → 使用 fastgpt 解析器
      - test_explicit_fastgpt_engine：传 engine=fastgpt → 与默认一致
      - test_mineru_engine_pdf：传 engine=mineru + PDF → 返回 ParseResult
      - test_mineru_engine_docx：传 engine=mineru + DOCX → 返回 ParseResult
      - test_mineru_unsupported_csv：传 engine=mineru + CSV → ValueError
      - test_mineru_unsupported_xlsx：传 engine=mineru + XLSX → ValueError
      - test_unknown_engine：传 engine=unknown → ValueError
    - `tests/test_mineru_client.py`:
      - test_placeholder_mode：无 MINERU_API_URL → 返回 placeholder 数据
      - test_placeholder_has_all_fields：placeholder 结果包含所有 ParseResult 字段
      - test_placeholder_raw_text_not_empty：raw_text 非空且包含 "MinerU"
  - TDD GREEN 阶段 — 确保所有测试通过（Task 1 的实现应已满足）
  - 如果有测试失败，修复 Task 1 的实现直到全部通过
  - 创建测试 fixtures：`tests/fixtures/test.pdf`（小文件）, `tests/fixtures/test.csv`

  **Must NOT do**:
  - 不修改现有解析器代码来通过测试
  - 不降低测试覆盖率要求

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: TDD 测试编写需要深入理解业务逻辑和边界条件
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4, 5)
  - **Blocks**: Task 7
  - **Blocked By**: Tasks 0, 1

  **References**:

  **Pattern References** (existing code to follow):
  - `knowledge-process-api/tests/test_health.py` — 已有冒烟测试模式（Task 0 创建）
  - `knowledge-process-api/tests/conftest.py` — 共享 fixtures

  **API/Type References** (contracts to test):
  - `knowledge-process-api/src/fastgpt_demo/parsers/__init__.py:29-58` — parse_file() 函数签名和调度逻辑
  - `knowledge-process-api/src/fastgpt_demo/parsers/mineru_parser.py` — MinerU 客户端（Task 1 创建）
  - `knowledge-process-api/src/fastgpt_demo/parsers/_types.py` — ParseResult 结构

  **WHY Each Reference Matters**:
  - `test_health.py` — 参考现有测试结构和 TestClient 使用模式
  - `parsers/__init__.py` — 需要测试的调度逻辑目标
  - `mineru_parser.py` — 需要测试的 MinerU 客户端

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All backend tests pass
    Tool: Bash
    Preconditions: 后端依赖已安装，Task 0 和 Task 1 完成
    Steps:
      1. cd knowledge-process-api && pytest tests/ -v
      2. Assert output shows all tests passed (no failures, no errors)
      3. Count total tests >= 8
    Expected Result: 所有测试通过，覆盖 engine 调度和 MinerU 客户端
    Failure Indicators: 任何测试失败或错误
    Evidence: .sisyphus/evidence/task-3-backend-tests.txt

  Scenario: Backward compatibility verified
    Tool: Bash (curl)
    Preconditions: 后端服务运行
    Steps:
      1. curl -s -F "file=@tests/fixtures/test.pdf" http://localhost:8000/api/parse > /tmp/default.json
      2. curl -s -F "file=@tests/fixtures/test.pdf" -F "engine=fastgpt" http://localhost:8000/api/parse > /tmp/explicit.json
      3. diff /tmp/default.json /tmp/explicit.json
      4. Assert no differences
    Expected Result: 默认和显式 fastgpt 结果完全一致
    Failure Indicators: diff 有输出
    Evidence: .sisyphus/evidence/task-3-backward-compat.txt
  ```

  **Commit**: YES
  - Message: `test(api): add TDD tests for engine dispatch and MinerU client`
  - Files: `knowledge-process-api/tests/test_engine_dispatch.py`, `knowledge-process-api/tests/test_mineru_client.py`, `knowledge-process-api/tests/fixtures/`

- [ ] 4. 前端 — 工具选择器 UI + 多引擎状态管理

  **What to do**:
  - 在 `KnowledgeProcessDemo.vue` 的 script 中添加状态：
    ```js
    // 工具选择器
    const selectedEngine = ref('fastgpt')
    const engineResults = ref({}) // { fastgpt: ParseResult | null, mineru: ParseResult | null }
    const MINERU_SUPPORTED_EXTS = ['pdf', 'docx', 'doc', 'pptx', 'png', 'jpg', 'jpeg', 'gif', 'webp']
    ```
  - 添加 computed `isMineruAvailable`：基于当前文件类型判断 MinerU 是否可用
  - 添加 computed `engines` 选项列表：
    ```js
    const engines = computed(() => {
      const list = [{ value: 'fastgpt', label: 'FastGPT 默认' }]
      if (isMineruAvailable.value) {
        list.push({ value: 'mineru', label: 'MinerU' })
      }
      return list
    })
    ```
  - 修改 `runParse()` 函数：发送 `engine` 参数到后端
    ```js
    formData.append('engine', selectedEngine.value)
    // 存储 result 到 engineResults[selectedEngine.value]
    ```
  - 在右侧选项面板的 "解析选项" 区域，在现有 parseMethod 下拉框**上方**添加引擎选择器：
    ```html
    <div class="demo-option-item">
      <span>解析引擎：</span>
      <select v-model="selectedEngine">
        <option v-for="e in engines" :key="e.value" :value="e.value">{{ e.label }}</option>
      </select>
    </div>
    ```
  - 当 MinerU 不可用时，显示提示文字
  - 修改 `processFile()`：切换文件时清除 `engineResults`，重置 `selectedEngine` 为 `'fastgpt'`
  - 修改下游函数（`runMarkdownConvert`, `runCleaning`, `runChunking`）：使用当前 `selectedEngine` 对应的解析结果

  **Must NOT do**:
  - 不提取子组件
  - 不重构现有代码结构
  - 不添加 localStorage 或缓存

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: 涉及 UI 组件添加和状态管理，需要保持视觉一致性
  - **Skills**: [`frontend-design`]
    - `frontend-design`: 确保工具选择器的视觉设计匹配现有 Demo 风格

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 3, 5)
  - **Blocks**: Tasks 5, 7
  - **Blocked By**: Task 1

  **References**:

  **Pattern References** (existing code to follow):
  - `apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue:183-203` — 现有 Step 0 Options 区域，工具选择器应放在 option-title 下方
  - `apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue:186-189` — 现有 parseMethod select 模式，完全复制这个 UI 模式
  - `apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue:483-507` — 现有 runParse() 函数，需要扩展

  **API/Type References** (contracts to implement against):
  - `knowledge-process-api/app.py:127-131` — 更新后的 API 接受 `engine` Form 参数

  **WHY Each Reference Matters**:
  - L183-203: 新工具选择器放在这个区域的 option-title 后面、parseMethod 前面
  - L186-189: select 的样式和 v-model 模式直接复用
  - L483-507: 需要在 FormData 中添加 engine 参数，并存储结果到 engineResults

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Tool selector renders correctly
    Tool: Bash (vitest)
    Preconditions: vitest 已配置
    Steps:
      1. Mount KnowledgeProcessDemo component
      2. Upload a PDF file (simulate file upload)
      3. Assert select element with engine options exists
      4. Assert default selected engine is 'fastgpt'
      5. Assert exactly 2 options visible (FastGPT 默认, MinerU)
    Expected Result: 工具选择器渲染，默认选中 FastGPT
    Failure Indicators: 选择器不存在，选项数量不对
    Evidence: .sisyphus/evidence/task-4-tool-selector.txt

  Scenario: MinerU disabled for unsupported file types
    Tool: Bash (vitest)
    Preconditions: vitest 已配置
    Steps:
      1. Mount component
      2. Upload a CSV file
      3. Assert engines list only has 'fastgpt' (MinerU not available)
      4. Assert selectedEngine auto-resets to 'fastgpt'
    Expected Result: CSV 文件时 MinerU 选项不可用
    Failure Indicators: MinerU 选项仍然显示
    Evidence: .sisyphus/evidence/task-4-mineru-disabled.txt

  Scenario: runParse sends engine parameter
    Tool: Bash (vitest + fetch mock)
    Preconditions: 组件已 mount，文件已上传
    Steps:
      1. Set selectedEngine to 'mineru'
      2. Click parse button
      3. Assert fetch was called with FormData containing engine='mineru'
    Expected Result: API 请求包含正确的 engine 参数
    Failure Indicators: FormData 中没有 engine 字段
    Evidence: .sisyphus/evidence/task-4-engine-param.txt
  ```

  **Commit**: YES
  - Message: `feat(demo): add tool selector UI and multi-engine state management`
  - Files: `apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue`

- [ ] 5. 前端 — 左右并排结果对比视图

  **What to do**:
  - 在 `KnowledgeProcessDemo.vue` 的 Step 0 结果区域实现并排对比布局：
    - 修改 `.demo-result-panel` 的内部结构：
      ```html
      <div class="compare-view" v-if="hasMultipleResults">
        <div class="compare-column">
          <div class="compare-label">FastGPT 默认</div>
          <div class="compare-content">... FastGPT 结果 ...</div>
        </div>
        <div class="compare-column">
          <div class="compare-label">MinerU</div>
          <div class="compare-content">... MinerU 结果 ...</div>
        </div>
      </div>
      ```
    - 当只有当前引擎结果时，保持现有单栏显示
    - 当两个引擎都有结果时，自动切换为左右并排
  - 添加并排对比 CSS：
    ```css
    .compare-view { display: flex; gap: 16px; }
    .compare-column { flex: 1; min-width: 0; }
    .compare-label { /* 匹配现有 result-label 风格 */ }
    .compare-content { /* 匹配现有 result-content 风格 */ }
    ```
  - 添加 `hasMultipleResults` computed：检查 engineResults 中是否有超过 1 个非空结果
  - 在 stats-bar 中添加对比统计：两个工具的字符数对比
  - 响应式处理：移动端 `.compare-view` 改为纵向堆叠

  **Must NOT do**:
  - 不实现 diff 高亮
  - 不添加质量评分
  - 不添加解析耗时显示

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: 纯 UI 布局和样式工作，需要保持视觉一致性
  - **Skills**: [`frontend-design`]
    - `frontend-design`: 确保并排对比布局的视觉质量

  **Parallelization**:
  - **Can Run In Parallel**: YES (但依赖 Task 4 的状态管理)
  - **Parallel Group**: Wave 2 (with Tasks 3, 4) — 注意实际执行需在 Task 4 之后
  - **Blocks**: Tasks 6, 7
  - **Blocked By**: Task 4

  **References**:

  **Pattern References** (existing code to follow):
  - `apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue:96-104` — 现有 Step 0 结果显示区域
  - `apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue:57-94` — 现有 stats-bar 结构
  - `apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue:772-798` — 现有 layout CSS

  **WHY Each Reference Matters**:
  - L96-104: 需要修改这个区域，在 parsedResult 展示之外添加对比视图
  - L57-94: 需要扩展 stats-bar 添加对比统计
  - L772-798: 现有布局 CSS 需要扩展并排对比样式

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Side-by-side comparison renders
    Tool: Bash (vitest)
    Preconditions: Task 4 完成，组件已 mount
    Steps:
      1. Upload a PDF file
      2. Set selectedEngine to 'fastgpt', trigger parse (mock API response)
      3. Set selectedEngine to 'mineru', trigger parse (mock API response)
      4. Assert DOM contains '.compare-view' element
      5. Assert 2 '.compare-column' elements exist
      6. Assert each column has content
    Expected Result: 并排对比视图正确渲染，两栏各有内容
    Failure Indicators: 单栏显示、缺少某列、内容为空
    Evidence: .sisyphus/evidence/task-5-compare-view.txt

  Scenario: Single result shows normal view
    Tool: Bash (vitest)
    Preconditions: 组件已 mount
    Steps:
      1. Upload a PDF file
      2. Parse with 'fastgpt' only
      3. Assert '.compare-view' does NOT exist
      4. Assert normal result-content display
    Expected Result: 只有一个工具结果时，保持原有单栏显示
    Failure Indicators: 显示了空的对比视图
    Evidence: .sisyphus/evidence/task-5-single-result.txt

  Scenario: Responsive layout on narrow screen
    Tool: Bash (vitest)
    Preconditions: 对比视图已渲染
    Steps:
      1. Upload PDF, parse with both engines
      2. Set viewport width to 768px
      3. Assert .compare-view has flex-direction: column
    Expected Result: 窄屏时自动切换为上下堆叠
    Failure Indicators: 仍然左右排列导致溢出
    Evidence: .sisyphus/evidence/task-5-responsive.txt
  ```

  **Commit**: YES
  - Message: `feat(demo): add side-by-side comparison view for parsing results`
  - Files: `apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue`

- [ ] 6. 前端测试 — TDD: 工具选择器 + 对比视图

  **What to do**:
  - TDD RED 阶段 — 扩展 `tests/KnowledgeProcessDemo.test.js`：
    - test_tool_selector_renders_with_pdf：上传 PDF → 工具选择器显示 2 个选项
    - test_tool_selector_disables_mineru_for_csv：上传 CSV → 只显示 FastGPT
    - test_default_engine_is_fastgpt：默认选中 FastGPT
    - test_switching_engine_updates_state：切换引擎 → selectedEngine 更新
    - test_parse_sends_engine_param：解析时 FormData 包含 engine 参数
    - test_both_results_persist：解析两个工具后 → 两个结果都在 state 中
    - test_file_change_clears_results：切换文件 → 两个工具结果都清空
    - test_compare_view_shows_both：两个结果存在 → 并排对比视图渲染
    - test_single_result_no_compare：只有一个结果 → 正常单栏显示
  - TDD GREEN 阶段 — 确保所有测试通过（Task 4, 5 的实现应已满足）
  - 如果有测试失败，修复 Task 4/5 的实现直到全部通过

  **Must NOT do**:
  - 不降低测试覆盖率
  - 不跳过任何测试用例

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 组件测试编写需要理解 Vue test-utils 和业务逻辑
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (with Task 7，但 Task 7 需等 Task 6)
  - **Blocks**: Task 7
  - **Blocked By**: Tasks 2, 5

  **References**:

  **Pattern References** (existing code to follow):
  - `apps/knowledge-process-demo/tests/KnowledgeProcessDemo.test.js` — Task 2 创建的冒烟测试
  - `apps/knowledge-process-demo/src/views/KnowledgeProcessDemo.vue` — 被测试的组件

  **External References**:
  - @vue/test-utils: `https://test-utils.vuejs.org/guide/`
  - vitest API: `https://vitest.dev/api/`

  **WHY Each Reference Matters**:
  - 冒烟测试文件 — 在其基础上扩展更多测试用例
  - 组件文件 — 需要理解组件的所有 ref/computed/method 来编写有意义的测试

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All frontend tests pass
    Tool: Bash
    Preconditions: vitest 已配置，Tasks 2, 4, 5 完成
    Steps:
      1. cd apps/knowledge-process-demo && pnpm test
      2. Assert output shows all tests passed
      3. Count total tests >= 9
    Expected Result: 所有前端测试通过
    Failure Indicators: 任何测试失败或错误
    Evidence: .sisyphus/evidence/task-6-frontend-tests.txt
  ```

  **Commit**: YES
  - Message: `test(demo): add component tests for tool selector and comparison view`
  - Files: `apps/knowledge-process-demo/tests/KnowledgeProcessDemo.test.js`

- [ ] 7. 集成验证 — 全流程测试

  **What to do**:
  - 启动后端服务（`uv run uvicorn app:app --port 8000`）
  - 用 curl 执行完整的端到端测试：
    1. 上传 PDF + engine=fastgpt → 验证 ParseResponse 结构完整
    2. 上传 PDF + engine=mineru → 验证 placeholder 结果
    3. 上传 CSV + engine=mineru → 验证 422 错误
    4. 不传 engine → 验证向后兼容
  - 启动前端 dev server，验证：
    1. 工具选择器可见
    2. 上传 PDF 后 MinerU 选项可用
    3. 上传 CSV 后 MinerU 选项不可用
    4. 两个工具分别解析后，并排对比视图显示
  - 运行 `pytest` + `vitest` 全部通过
  - 更新 AGENTS.md 中 API 接口规范，添加 engine 参数文档

  **Must NOT do**:
  - 不修复集成中发现的问题（记录并创建后续任务）
  - 不做性能测试

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: 全流程集成测试需要同时理解前后端，排查问题
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (sequential after Task 6)
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 3, 4, 5, 6

  **References**:

  **Pattern References** (existing code to follow):
  - `AGENTS.md` — API 接口规范部分，需要更新添加 engine 参数

  **API/Type References** (contracts to verify):
  - `knowledge-process-api/app.py:127-146` — 更新后的 /api/parse 端点
  - `knowledge-process-api/src/fastgpt_demo/parsers/_types.py` — ParseResponse 结构

  **WHY Each Reference Matters**:
  - `AGENTS.md` — 需要更新 API 文档反映新的 engine 参数
  - 端点代码 — 需要验证实际行为与文档一致

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Full backend integration
    Tool: Bash (curl)
    Preconditions: 后端服务运行在 localhost:8000
    Steps:
      1. curl -s -F "file=@tests/fixtures/test.pdf" http://localhost:8000/api/parse | python -c "import sys,json; d=json.load(sys.stdin); assert 'raw_text' in d; print('OK')"
      2. curl -s -F "file=@tests/fixtures/test.pdf" -F "engine=fastgpt" http://localhost:8000/api/parse | python -c "import sys,json; d=json.load(sys.stdin); assert d['raw_text']; print('OK')"
      3. curl -s -F "file=@tests/fixtures/test.pdf" -F "engine=mineru" http://localhost:8000/api/parse | python -c "import sys,json; d=json.load(sys.stdin); assert 'MinerU' in d['raw_text']; print('OK')"
      4. curl -s -w "%{http_code}" -F "file=@tests/fixtures/test.csv" -F "engine=mineru" http://localhost:8000/api/parse | grep -E "4[0-9]{2}"
    Expected Result: 所有 curl 断言通过
    Failure Indicators: 任何 curl 返回非预期结果
    Evidence: .sisyphus/evidence/task-7-integration.txt

  Scenario: All test suites pass
    Tool: Bash
    Preconditions: 所有代码已就位
    Steps:
      1. cd knowledge-process-api && pytest tests/ -v
      2. cd apps/knowledge-process-demo && pnpm test
      3. Assert both commands report all tests passed
    Expected Result: pytest 和 vitest 全部通过
    Failure Indicators: 任何测试失败
    Evidence: .sisyphus/evidence/task-7-all-tests.txt
  ```

  **Commit**: YES
  - Message: `test(integration): full flow verification and update API docs`
  - Files: `AGENTS.md`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `pytest` + `vitest` + linter. Review all changed files for: type errors, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration. Test edge cases: empty state, invalid input, unsupported file type. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built, nothing beyond spec was built. Check "Must NOT do" compliance. Detect cross-task contamination. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `test(infra): add pytest configuration and fixtures` — knowledge-process-api/tests/conftest.py, pytest.ini
- **Wave 1**: `feat(api): add engine parameter to /api/parse with MinerU placeholder` — app.py, parsers/mineru_parser.py, parsers/__init__.py
- **Wave 1**: `test(infra): add vitest configuration for frontend` — apps/knowledge-process-demo/vitest.config.js
- **Wave 2**: `test(api): add TDD tests for engine dispatch and MinerU client` — tests/test_engine_dispatch.py, tests/test_mineru_client.py
- **Wave 2**: `feat(demo): add tool selector UI and multi-engine state management` — KnowledgeProcessDemo.vue
- **Wave 2**: `feat(demo): add side-by-side comparison view for parsing results` — KnowledgeProcessDemo.vue
- **Wave 3**: `test(demo): add component tests for tool selector and comparison view` — tests/
- **Wave 3**: `test(integration): full flow verification with curl and vitest` — tests/

---

## Success Criteria

### Verification Commands
```bash
# Backend tests
cd knowledge-process-api && pytest tests/ -v  # Expected: all pass

# Frontend tests
cd apps/knowledge-process-demo && npx vitest run  # Expected: all pass

# API backward compatibility
curl -F "file=@test.pdf" http://localhost:8000/api/parse | jq .raw_text  # Expected: same as before

# Engine parameter
curl -F "file=@test.pdf" -F "engine=fastgpt" http://localhost:8000/api/parse | jq .raw_text  # Expected: same as above

# MinerU engine
curl -F "file=@test.pdf" -F "engine=mineru" http://localhost:8000/api/parse | jq .raw_text  # Expected: placeholder text

# Unsupported type
curl -F "file=@test.csv" -F "engine=mineru" http://localhost:8000/api/parse  # Expected: 422 error
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass (pytest + vitest)
- [ ] Backward compatibility preserved (no engine param = same behavior)
- [ ] MinerU placeholder returns realistic mock data
- [ ] Both tool results coexist in frontend state
- [ ] Unsupported file types properly handled (422 + disabled selector)
