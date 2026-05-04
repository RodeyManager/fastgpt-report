# 项目文档索引

> **项目**: fastgpt-report / knowledge-process-api
> **最后更新**: 2026-05-03

---

## 文档结构

```
docs/
├── README.md                                              ← 本文件
├── project-phase-analysis.md                              ← 项目阶段总览
└── superpowers/
    ├── specs/                                             ← 功能规范 / 设计文档
    │   ├── 2026-04-30-p0-data-cleaning-optimization.md    ← P0 基础清洗优化
    │   ├── 2026-04-30-p1-data-cleaning-optimization.md    ← P1 结构级清洗优化
    │   ├── 2026-04-30-clean-rule-tooltip-design.md        ← 清洗规则浮窗说明
    │   └── 2026-05-01-data-cleaning-implementation-plan.md← P2 清洗规则全景规划
    └── plans/                                             ← 执行计划
        ├── 2026-05-01-p2-data-cleaning-rules.md           ← P2 清洗规则实施计划
        └── 2026-05-01-opendataloader-pdf-integration.md   ← OpenDataLoader-PDF 集成
```

## 按阶段查阅

| 阶段 | 规范文档 | 执行计划 | 完成度 |
|------|---------|---------|--------|
| **P0** 基础清洗规则 | [specs/P0](./superpowers/specs/2026-04-30-p0-data-cleaning-optimization.md) | — | ✅ 100% |
| **P1** 结构级清洗 | [specs/P1](./superpowers/specs/2026-04-30-p1-data-cleaning-optimization.md) | — | ✅ 100% |
| **P2** Profile 预设 + HTML 过滤 | [specs/P2](./superpowers/specs/2026-05-01-data-cleaning-implementation-plan.md) | [plans/P2](./superpowers/plans/2026-05-01-p2-data-cleaning-rules.md) | ✅ 100% |
| **OpenDataLoader-PDF** 引擎 | — | [集成计划](./superpowers/plans/2026-05-01-opendataloader-pdf-integration.md) | ✅ 100% |
| **P3** 专用分块 + 语义增强 | 见 [project-phase-analysis.md](./project-phase-analysis.md#十p3-阶段规划) | — | ⏳ 规划中 |

## 项目总览

详见 [project-phase-analysis.md](./project-phase-analysis.md)，包含：

- P0-P2 各阶段完成度逐项验证
- 当前测试覆盖（234 passed, 0 failed）
- P3 阶段规划（8 种专用分块 + 3 种语义增强）
- 能力全景与下一步行动建议
