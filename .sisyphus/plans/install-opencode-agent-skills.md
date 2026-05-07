# 安装 opencode-agent-skills 插件

## TL;DR

> **Quick Summary**: 在 OpenCode 全局配置中添加 `opencode-agent-skills` 插件，使技能功能在所有项目中可用
>
> **Deliverables**: OpenCode 配置更新，插件加载成功
> **Estimated Effort**: Trivial (< 5 分钟)
> **Parallel Execution**: NO - 顺序执行
> **Critical Path**: 确认配置文件路径 → 编辑配置 → 重启 OpenCode

---

## Context

### Original Request
用户希望安装 OpenCode 平台的 `opencode-agent-skills` 插件到全局环境。

### Research Findings
- **插件名**: `opencode-agent-skills` (npm)
- **功能**: 提供动态 AI Agent 技能加载工具
- **安装方式**: 在 `opencode.json` 的 `plugin` 数组中添加包名
- **全局配置路径**: `~/.config/opencode/opencode.json`
- **插件缓存目录**: `~/.cache/opencode/node_modules/`
- **重启**: OpenCode 启动时自动通过 Bun 安装并加载

---

## Work Objectives

### Core Objective
在 OpenCode 全局配置中注册 `opencode-agent-skills` 插件。

### Must Have
- [ ] `~/.config/opencode/opencode.json` 包含 `"plugin": ["opencode-agent-skills"]`
- [ ] OpenCode 重启后可识别该插件

### Must NOT Have
- 不要修改项目级配置文件
- 不要手动创建 package.json（Bun 自动处理）

---

## Verification Strategy

### QA Policy
- 检查配置文件 JSON 语法正确
- 验证插件名称拼写无误

---

## TODOs

- [ ] 1. 读取/创建全局 OpenCode 配置文件

  **What to do**:
  - 读取 `~/.config/opencode/opencode.json`
  - 如果文件不存在，检查目录 `~/.config/opencode/` 是否存在

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单文件读写操作
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `git-master`: 不涉及 git 操作

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 2
  - **Blocked By**: None

  **References**:
  - OpenCode 官方文档: https://opencode.ai/docs/plugins/
  - npm 包: https://registry.npmjs.org/opencode-agent-skills

  **Acceptance Criteria**:
  - [ ] 文件路径存在或已创建目录结构
  - [ ] 能够读取到文件内容（或确认需要新建）

  **QA Scenarios**:

  \`\`\`
  Scenario: 读取现有配置文件
    Tool: Bash
    Preconditions: 配置文件已存在
    Steps:
      1. Read ~/.config/opencode/opencode.json
      2. 检查是否已有 "plugin" 字段
    Expected Result: 文件内容正确返回，JSON 格式有效
    Failure Indicators: 文件不存在或 JSON 格式错误
    Evidence: 读取结果

  Scenario: 确认目录结构
    Tool: Bash
    Preconditions: 配置文件不存在
    Steps:
      1. Check if ~/.config/opencode/ directory exists
    Expected Result: 确认目录状态
    Failure Indicators: 目录不存在
    Evidence: ls 输出
  \`\`\`

  **Commit**: NO

- [ ] 2. 更新配置文件添加插件

  **What to do**:
  - 如果 `"plugin"` 字段已存在，追加 `"opencode-agent-skills"` 到数组
  - 如果 `"plugin"` 字段不存在，创建该字段
  - 如果文件不存在，创建包含插件配置的基础 JSON

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 简单 JSON 编辑操作
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `git-master`: 不涉及 git 操作

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: None (最终步骤)
  - **Blocked By**: Task 1

  **References**:
  - OpenCode 插件配置格式:
    ```json
    {
      "plugin": ["opencode-agent-skills"]
    }
    ```

  **Acceptance Criteria**:
  - [ ] 配置文件中包含 `"plugin": ["opencode-agent-skills"]`
  - [ ] JSON 语法正确（无尾逗号等）

  **QA Scenarios**:

  \`\`\`
  Scenario: 验证配置更新成功
    Tool: Bash
    Preconditions: 配置文件已更新
    Steps:
      1. Read ~/.config/opencode/opencode.json
      2. 验证 JSON.parse() 可正常解析
      3. 确认 "opencode-agent-skills" 在 plugin 数组中
    Expected Result: JSON 有效且插件已注册
    Failure Indicators: 解析错误或插件名不在数组中
    Evidence: 读取的配置内容
  \`\`\`

  **Commit**: NO

---

## Final Verification Wave

> 无需 Final Verification Wave - 步骤简单可验证

---

## Success Criteria

### Verification Commands
```bash
# 验证配置文件存在且有效
cat ~/.config/opencode/opencode.json | jq .
```

### Final Checklist
- [ ] `~/.config/opencode/opencode.json` 存在
- [ ] JSON 格式有效
- [ ] `"opencode-agent-skills"` 在 `"plugin"` 数组中
- [ ] 下次启动 OpenCode 时插件将被自动加载

---

## Next Steps for User

配置完成后，重启 OpenCode 即可自动安装并加载插件。
