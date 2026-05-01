# 清洗规则浮窗说明 — 规划文档

> **项目**: fastgpt-report / knowledge-process-demo
> **日期**: 2026-04-30
> **目标**: 为每条清洗规则增加悬停浮窗说明，完善规则解释

***

## 1. 现状分析

### 1.1 当前 UI 结构

清洗选项面板位于 `KnowledgeProcessDemo.vue` 的 Step 2 区域，结构如下：

```
option-title: "清洗选项"
├── demo-option-item × 8 (checkbox + 标签文本)
├── 分隔线 + "高级选项"
├── demo-option-item × 2 (checkbox + 标签文本)
├── demo-action-btn: "执行清洗"
└── highlight-block: 4 条规则的简要说明
```

### 1.2 存在的问题

1. **规则说明不完整**：底部 `highlight-block` 仅覆盖 4 条规则（NFKC、不可见字符、脱敏、特殊字符过滤），缺少其余 6 条
2. **说明与选项分离**：用户需要上下扫视才能关联规则和说明
3. **说明内容过于简略**：缺少示例输入/输出，用户无法直观理解规则效果

***

## 2. 设计方案

### 2.1 交互设计

在每条规则的标签文本后添加 `ℹ` 图标按钮，鼠标悬停时显示浮窗（CSS-only tooltip），包含：
- **规则说明**：一句话描述规则作用
- **示例**：输入 → 输出的对比展示

```
┌─────────────────────────────────────────┐
│ ☑ Unicode NFKC 标准化  ℹ               │
│                         ┌──────────────┐│
│                         │ 统一全角/半角 ││
│                         │ 字符和兼容性 ││
│                         │ 字符         ││
│                         │              ││
│                         │ 示例:        ││
│                         │ ＡＢＣ→ABC   ││
│                         │ １２３→123   ││
│                         │ ①②③→123     ││
│                         └──────────────┘│
└─────────────────────────────────────────┘
```

### 2.2 技术方案

**纯 CSS 实现**，零依赖：

- 使用 `position: relative` 容器 + `position: absolute` 浮窗
- 默认 `opacity: 0; visibility: hidden`，悬停时 `opacity: 1; visibility: visible`
- 浮窗定位在图标右侧，避免遮挡其他选项
- 响应式：小屏幕时浮窗宽度自适应

### 2.3 数据结构

将规则说明抽取为 JS 常量数组，便于维护：

```js
const CLEAN_RULE_DESCRIPTIONS = {
  trim: {
    title: '去除首尾空白',
    desc: '移除文本开头和结尾的空白字符（空格、Tab、换行等）',
    examples: ['  hello  → hello', '\t文本\t → 文本']
  },
  normalize_unicode: {
    title: 'Unicode NFKC 标准化',
    desc: '使用 NFKC 形式统一全角/半角字符和兼容性字符，确保文本检索一致性',
    examples: ['ＡＢＣ → ABC', '１２３ → 123', '！？ → !?', '①②③ → 123', 'ﬁ → fi']
  },
  remove_invisible_chars: {
    title: '移除不可见字符',
    desc: '移除零宽空格、BOM、软连字符等不可见但影响文本匹配的 Unicode 字符',
    examples: ['hello\\u200Bworld → helloworld', '\\uFEFF文本 → 文本', 'soft\\u00ADhyphen → softhyphen']
  },
  remove_chinese_space: {
    title: '移除中文字符间空格',
    desc: '移除中文字符之间的多余空格，保留中英文混排时的必要空格',
    examples: ['你好 世界 → 你好世界', 'hello 世界 → hello 世界']
  },
  normalize_newline: {
    title: '规范化换行符',
    desc: '将 Windows (\\r\\n) 和旧 Mac (\\r) 换行符统一为 Unix 格式 (\\n)',
    examples: ['行1\\r\\n行2 → 行1\\n行2', '行1\\r行2 → 行1\\n行2']
  },
  fix_hyphenation: {
    title: '连字符断行修复',
    desc: '修复 PDF 提取中因断行产生的连字符分割，还原完整单词',
    examples: ['com-\\nputer → computer', 'awe-\\nsome → awesome']
  },
  collapse_whitespace: {
    title: '合并连续空白',
    desc: '将 2 个及以上连续非换行空白字符合并为 1 个空格',
    examples: ['hello    world → hello world', 'a  \\t  b → a b']
  },
  remove_empty_lines: {
    title: '移除空行',
    desc: '将 3 行及以上连续换行压缩为 2 行（保留段落分隔）',
    examples: ['行1\\n\\n\\n\\n行2 → 行1\\n\\n行2']
  },
  mask_sensitive: {
    title: '敏感信息脱敏',
    desc: '使用占位符替换手机号、邮箱、身份证号、IP 地址等敏感信息',
    examples: ['13812345678 → ***PHONE***', 'test@mail.com → ***EMAIL***', '110101199001011234 → ***IDCARD***', '192.168.1.1 → ***IP***']
  },
  filter_special_chars: {
    title: '特殊字符过滤（白名单）',
    desc: '仅保留中文、英文、数字、常用标点和括号，移除异常符号和乱码字符',
    examples: ['你好★世界 → 你好世界', 'test♦123 → test123', '中文，标点！ → 中文，标点！']
  }
}
```

### 2.4 模板结构变更

将每条规则的 `demo-option-item` 从：

```html
<div class="demo-option-item">
  <input type="checkbox" v-model="cleanOptions.trim" />
  <span>去除首尾空白</span>
</div>
```

改为：

```html
<div class="demo-option-item">
  <input type="checkbox" v-model="cleanOptions.trim" />
  <span>去除首尾空白</span>
  <span class="rule-info-trigger" tabindex="0">ℹ
    <span class="rule-info-tooltip">
      <span class="tooltip-desc">移除文本开头和结尾的空白字符</span>
      <span class="tooltip-examples">
        <span class="example-label">示例</span>
        <span class="example-item">  hello  → hello</span>
      </span>
    </span>
  </span>
</div>
```

### 2.5 样式设计

```css
.rule-info-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  font-size: 0.65rem;
  cursor: help;
  position: relative;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.rule-info-trigger:hover {
  background: var(--accent-cyan);
  color: #fff;
}

.rule-info-tooltip {
  position: absolute;
  left: calc(100% + 8px);
  top: 50%;
  transform: translateY(-50%);
  width: 260px;
  padding: 10px 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  z-index: 100;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  pointer-events: none;
}

.rule-info-trigger:hover .rule-info-tooltip,
.rule-info-trigger:focus .rule-info-tooltip {
  opacity: 1;
  visibility: visible;
}

.tooltip-desc {
  display: block;
  font-size: 0.78rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 6px;
}

.tooltip-examples {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.example-label {
  font-size: 0.7rem;
  color: var(--accent-cyan);
  font-weight: 500;
  margin-bottom: 2px;
}

.example-item {
  font-size: 0.72rem;
  font-family: var(--font-mono);
  color: var(--text-muted);
  line-height: 1.5;
}
```

### 2.6 移除底部 highlight-block

将当前底部的 `highlight-block` 说明区域移除，因为所有规则说明已内联到浮窗中。

***

## 3. 变更范围

| 文件 | 变更内容 |
|------|---------|
| `KnowledgeProcessDemo.vue` `<script setup>` | 新增 `CLEAN_RULE_DESCRIPTIONS` 常量 |
| `KnowledgeProcessDemo.vue` `<template>` | 每条规则的 `demo-option-item` 增加 `ℹ` 图标和浮窗；移除底部 `highlight-block` |
| `KnowledgeProcessDemo.vue` `<style scoped>` | 新增 `.rule-info-trigger`、`.rule-info-tooltip`、`.tooltip-desc`、`.tooltip-examples`、`.example-label`、`.example-item` 样式 |

***

## 4. 各规则浮窗内容

### 4.1 基础选项

| 规则 | 说明 | 示例 |
|------|------|------|
| 去除首尾空白 | 移除文本开头和结尾的空白字符（空格、Tab、换行等） | `  hello  ` → `hello` |
| Unicode NFKC 标准化 | 使用 NFKC 形式统一全角/半角字符和兼容性字符，确保文本检索一致性 | `ＡＢＣ` → `ABC`，`１２３` → `123`，`①②③` → `123`，`ﬁ` → `fi` |
| 移除不可见字符 | 移除零宽空格(U+200B)、BOM(U+FEFF)、软连字符(U+00AD)等不可见但影响匹配的字符 | `hello​world` → `helloworld`，`﻿文本` → `文本` |
| 移除中文字符间空格 | 移除中文字符之间的多余空格，保留中英文混排时的必要空格 | `你好 世界` → `你好世界`，`hello 世界` → `hello 世界` |
| 规范化换行符 | 将 Windows(\r\n) 和旧 Mac(\r) 换行符统一为 Unix 格式(\n) | `行1\r\n行2` → `行1\n行2` |
| 连字符断行修复 | 修复 PDF 提取中因断行产生的连字符分割，还原完整单词 | `com-\nputer` → `computer`，`awe-\nsome` → `awesome` |
| 合并连续空白 | 将 2 个及以上连续非换行空白字符合并为 1 个空格 | `hello    world` → `hello world` |
| 移除空行 | 将 3 行及以上连续换行压缩为 2 行，保留段落分隔 | `行1\n\n\n\n行2` → `行1\n\n行2` |

### 4.2 高级选项

| 规则 | 说明 | 示例 |
|------|------|------|
| 敏感信息脱敏 | 使用占位符替换手机号、邮箱、身份证号、IP 地址等敏感信息（默认关闭） | `13812345678` → `***PHONE***`，`test@mail.com` → `***EMAIL***` |
| 特殊字符过滤（白名单） | 仅保留中文、英文、数字、常用标点和括号，移除异常符号和乱码字符（默认关闭） | `你好★世界` → `你好世界`，`中文，标点！` → `中文，标点！` |

***

## 5. 响应式适配

- **大屏（>768px）**：浮窗在图标右侧展开，宽度 260px
- **小屏（≤768px）**：浮窗宽度缩小至 200px，或改为下方展开（`top: 100%; left: 0`）

***

## 6. 无障碍

- `tabindex="0"`：支持键盘 Tab 聚焦
- `:focus` 伪类：聚焦时也显示浮窗
- `cursor: help`：提示用户可查看帮助信息
- `role="tooltip"` + `aria-describedby`：屏幕阅读器支持（可选增强）
