# 保险文档专用清洗规则设计

> **日期**: 2026-05-04
> **范围**: 新增 5 条保险专用清洗规则 + 增强 1 条敏感信息脱敏 + 新建 `insurance` CleanProfile
> **相关规划**: [project-phase-analysis.md](../../project-phase-analysis.md) 第九节

---

## 一、概述

在现有 22 条清洗规则的基础上，新增/增强 6 条保险专用规则，并新建 `insurance` CleanProfile，覆盖人身险条款、合同、费率表等保险特有文档的处理需求。

## 二、新增规则明细

### 规则 1：`normalize_clause_numbering` — 条款编号标准化

| 属性 | 值 |
|------|-----|
| 文件名 | `cleaners/rules/clause_numbering.py` |
| name | `normalize_clause_numbering` |
| 默认启用 | ✅ True |

**功能**：检测保险条款的层级编号体系，在原编号后附加层级标记 `[L1] [L2] [L3]`，不改变原始文本，便于下游分块时识别条款边界。

**检测的编号模式**：

| 层级 | 模式 | 示例 | 标记 |
|------|------|------|------|
| L1 | `第[零一二三四五六七八九十百0-9]+条` | 第三条、第12条 | `[L1]` |
| L1 | `第[零一二三四五六七八九十百0-9]+章` | 第一章 | `[L1]` |
| L1 | `第[零一二三四五六七八九十百0-9]+节` | 第二节 | `[L1]` |
| L2 | `[零一二三四五六七八九十]+、` | 一、二、 | `[L2]` |
| L2 | `（[零一二三四五六七八九十]+）` | （一）（二） | `[L2]` |
| L3 | `\d+\.\s` | 1. 2. | `[L3]` |
| L3 | `\d+\.\d+` | 1.1 1.2 | `[L3]` |
| L3 | `[①-⑳]` | ①②③ | `[L3]` |

**关键实现细节**：
- 仅在行首出现时标记（避免误伤正文中的"第一条"等引用）
- 标记追加在编号原文之后，不替换原文
- 示例：`第三十二条 保险责任` → `第三十二条[L1] 保险责任`

### 规则 2：`preserve_policy_meta` — 保单元数据保留

| 属性 | 值 |
|------|-----|
| 文件名 | `cleaners/rules/policy_meta.py` |
| name | `preserve_policy_meta` |
| 默认启用 | ✅ True |

**功能**：检测文本中的保单元数据（保单号、合同编号、投保单号），用语义标记包裹而非丢弃。

**检测模式**：

| 类型 | 正则模式 | 示例 |
|------|---------|------|
| 保单号 | `保单[号号][：:]\s*([A-Za-z0-9_-]{5,50})` | 保单号：P202406010001 |
| 合同编号 | `合同编号[：:]\s*([A-Za-z0-9_-]{5,50})` | 合同编号：HT20240601001 |
| 独立编号 | `([A-Z]{2,4}\d{8,20})` | P202406010001 |
| 投保单号 | `投保单号[：:]\s*([A-Za-z0-9_-]{5,50})` | 投保单号：T20240601001 |

**关键实现细节**：
- 匹配到的元数据用 `[META:policy_no]P202406010001[/META]` 包裹
- 不删除、不修改原始值，仅增加语义标签
- 与 `filter_page_numbers` 互斥：保单号可能被误判为页码（如 `P202406010001` 含数字），本规则在前执行可防止误删除

### 规则 3：`merge_broken_clauses` — 跨页条款合并

| 属性 | 值 |
|------|-----|
| 文件名 | `cleaners/rules/clause_merge.py` |
| name | `merge_broken_clauses` |
| 默认启用 | ✅ True |

**功能**：将因翻页被截断的条款文本重新合并为完整条款。

**问题示例**：
```
第三十二条 保险责任的免除
因下列原因造成被保险人身故的，保险人不承
                                      ← 此处被翻页截断
担给付保险金的责任：
一、投保人故意造成被保险人身故的；
```

**实现策略**：

1. 识别条款起始行：以 `第[零一二三四五六七八九十百0-9]+条` 开头的行
2. 逐行扫描，当某行不以标点结尾（不含 `。！？；：，、」』）"` 等）且不包含条款起始标记时，与下一行合并
3. 空白行被视为条款内部的分隔，不被合并（保留段落结构）
4. 合并后补充条款边界标记

### 规则 4：`mask_sensitive` 增强（保险模式）

| 属性 | 值 |
|------|-----|
| 文件名 | `cleaners/rules/sensitive.py`（修改现有文件） |
| 参数 | `insurance_mode: bool = False` |

**新增模式**：当 `insurance_mode=True` 时，使用保险场景的脱敏策略。

| 信息类型 | 脱敏前 | 脱敏后 | 策略 |
|---------|--------|--------|------|
| 保单号 | P202406010001 | `P**********001` | 保留前缀和后3位 |
| 身份证号 | 310115199001011234 | `310***********1234` | 保留前3后4 |
| 银行卡号 | 6222021234567890 | `6222**********7890` | 保留前4后4 |
| 手机号 | 13812345678 | `138****5678` | 保留前3后4 |
| 姓名 | 张三 | `张*` | 保留姓氏 |
| 邮箱 | zhangsan@example.com | `z*******@example.com` | 保留首字符 |

**与通用模式的关系**：
- `insurance_mode=False` → 使用原有 7 种通用模式（身份证→`***IDCARD***`）
- `insurance_mode=True` → 使用保险专项脱敏（身份证→`310***********1234`，保留部分信息以便核保核赔场景使用）

### 规则 5：`fix_ocr_numbering` — OCR 编号修复

| 属性 | 值 |
|------|-----|
| 文件名 | `cleaners/rules/ocr_fix.py` |
| name | `fix_ocr_numbering` |
| 默认启用 | ✅ True |

**功能**：修复扫描件 OCR 识别后的条款编号错误。

**修复映射表**（仅在条款编号上下文中生效）：

| OCR 错误 | 修正 | 上下文要求 |
|---------|------|-----------|
| 小写 `l` → 数字 `1` | `第 l2 条` → `第 12 条` | 位于 `第` 和 `条` 之间、后面跟数字 |
| 字母 `O` → 数字 `0` | `第 1O 条` → `第 10 条` | 位于条款编号位置 |
| 英文逗号 `,` → 中文顿号 `、` | `一,` → `一、` | 跟在中文序号后 |
| 英文句号 `.` → 中文顿号 `、` | `一.` → `一、` | 跟在单一中文序号后（不含子序号 `1.1`） |
| 字母 `o` → 数字 `0` | `第 o 条` → `第 0 条`（少见） | 同上 |

**关键实现细节**：
- 仅在条款编号上下文中修复（`第X条`、`第X款`、`X、`、`（X）`），避免误伤正文
- 处理顺序：先`l→1`，再`O→0`（避免 `10` 被当作 `1O` 反向处理）

### 规则 6：`clean_insurance_table` — 保险表格专项清洗

| 属性 | 值 |
|------|-----|
| 文件名 | `cleaners/rules/insurance_table.py` |
| name | `clean_insurance_table` |
| 默认启用 | ❌ False |

**功能**：在 `clean_table` 基础上增加保险表格的特殊处理。

**与 `clean_table` 的差异**：

| 处理项 | clean_table | clean_insurance_table |
|--------|-------------|----------------------|
| 空行移除 | ✅ | ✅ |
| 空列移除 | ✅ | ✅ |
| 注释行（"注："/"说明："） | ❌ 可能被移除 | ✅ 保留 |
| 合计行（含"合计"/"总计"） | ❌ 无特殊处理 | ✅ 保留 |
| 合并单元格 | ❌ 无 | ✅ 检测并展开 |

**注意**：本规则应在 `clean_table` 之后运行（两个规则独立，但本规则假设表格基础结构已清洗）。

---

## 三、新建 CleanProfile：`insurance`

**文件**：`cleaners/profiles/insurance.py`

```python
insurance_rules = {
    # --- 继承 default 的 12 条默认启用 ---
    "trim": True, "normalize_unicode": True, "remove_invisible_chars": True,
    "remove_chinese_space": True, "normalize_newline": True, "fix_hyphenation": True,
    "collapse_whitespace": True, "remove_empty_lines": True,
    "clean_markdown_links": True, "remove_md_escapes": True, "clean_md_structure": True,

    # --- 保险专用规则默认启用 ---
    "normalize_clause_numbering": True,   # 新增
    "preserve_policy_meta": True,         # 新增
    "merge_broken_clauses": True,          # 新增
    "fix_ocr_numbering": True,            # 新增

    # --- P1/P2 规则调整 ---
    "filter_watermark": True,             # 扫描件常见"草稿"水印
    "filter_page_numbers": True,          # 但要保留保单号
    "process_footnotes": True,            # 免责说明等脚注
    "clean_table": True,                  # 表格基础清洗

    # --- 保持关闭 ---
    "deduplicate_paragraphs": False,      # 不同险种的重复条款是正常的
    "mask_sensitive": False,              # 默认关闭
    "filter_toc": False,                  # 目录有导航价值
    "filter_special_chars": False,
    "clean_insurance_table": False,       # 按需开启
    "remove_html_comments": False,
    "normalize_html_entities": False,
    "filter_html_noise": False,
}

insurance_params = {
    "footnote_action": "keep",            # 脚注保留
}
```

---

## 四、文件变更清单

| 操作 | 文件 | 说明 |
|------|------|------|
| ➕ 新增 | `cleaners/rules/clause_numbering.py` | 规则 1 |
| ➕ 新增 | `cleaners/rules/policy_meta.py` | 规则 2 |
| ➕ 新增 | `cleaners/rules/clause_merge.py` | 规则 3 |
| ✏️ 修改 | `cleaners/rules/sensitive.py` | 增强保险模式 |
| ➕ 新增 | `cleaners/rules/ocr_fix.py` | 规则 5 |
| ➕ 新增 | `cleaners/rules/insurance_table.py` | 规则 6 |
| ✏️ 修改 | `cleaners/rules/__init__.py` | 注册 6 条新规则 |
| ➕ 新增 | `cleaners/profiles/insurance.py` | 新建 Profile |
| ✏️ 修改 | `cleaners/profiles/__init__.py` | 注册 Profile |
| ➕ 新增 | `tests/cleaners/test_clause_numbering_rule.py` | 测试 1 |
| ➕ 新增 | `tests/cleaners/test_policy_meta_rule.py` | 测试 2 |
| ➕ 新增 | `tests/cleaners/test_clause_merge_rule.py` | 测试 3 |
| ✏️ 修改 | `tests/cleaners/test_sensitive_enhanced.py` | 追加保险模式测试 |
| ➕ 新增 | `tests/cleaners/test_ocr_fix_rule.py` | 测试 5 |
| ➕ 新增 | `tests/cleaners/test_insurance_table_rule.py` | 测试 6 |
| ✏️ 修改 | `tests/cleaners/test_clean_profile.py` | 追加 insurance Profile 测试 |
| ✏️ 修改 | `docs/project-phase-analysis.md` | 更新清洗规则清单 |
