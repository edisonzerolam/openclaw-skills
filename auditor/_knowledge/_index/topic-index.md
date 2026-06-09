# auditor 主题索引

> 主题 → 文件映射，供按领域快速查找
> 格式：主题 → [文件列表]（≤3行说明）
> 版本：v1.0 | 2026-05-22

---

## 1. 核心框架

### 目标分类（Phase-G）
- `SKILL.md` — G1-G5 目标分类框架，7 种变更类型
- `_knowledge/core-principles/auditor-principles.md` — P1 先读再改原则

### 执行框架（Phase-S）
- `SKILL.md` — S1-S5 执行框架详细说明
- `_knowledge/_enhancement/knowledge-enhancement-audit.md` — 知识增强审计框架

### 质量门（Layer0 Q-Gate）
- `SKILL.md` — Q0-Q6 质量门速查
- `_knowledge/_components/s1-quality-attributes.md` — K 层 S1 质量属性

### 版本治理（Phase-D）
- `SKILL.md` (Phase-D) — 版本治理与变更追踪

---

## 2. 增强层（A-L）

| 增强层 | 主题 | 映射文件 |
|--------|------|---------|
| A | CI/CD 集成 | `_knowledge/references/ci-cd-integration.md` |
| A | Skill 审计套件 | `_knowledge/_components/skill-audit-suite/SKILL.md` |
| B | 行为规则检查 | `_knowledge/_components/behavior-checker.md` |
| C | Context 卫生 | `_knowledge/_components/context-hygiene.md` |
| D | Session 管理 | `_knowledge/_components/session-manager.md` |
| E | 规划修正 | `agent-planner SKILL.md` (外部) |
| F | 深度调研 | `deep-research SKILL.md` (外部) |
| G | 自我进化 | `_knowledge/_components/self-improving-integration.md` |
| H | 多 Agent 团队 | `agent-team` (外部) |
| I | 报告生成 | `docx/pptx skill` (外部) |
| J | 知识库 | `knowledge-base` (外部) |
| K | 质量属性 | `_knowledge/_components/s1-quality-attributes.md` |
| **L** | **财务合规** | `_knowledge/_components/financial-compliance.md` |

---

## 3. 知识工程

### 知识分层（L1-L4）
- `SKILL.md` (L1-L4 热温冷数据) — 知识分层模型
- `_knowledge/references/external/auditor-expert-knowledge.md` — 8 个专家知识来源

### 知识增强
- `_knowledge/_enhancement/knowledge-enhancement-audit.md` — 知识增强审计
- `_knowledge/_enhancement/enhancement-registry.md` — 增强层注册表

### 知识索引
- `_knowledge/_index/keyword-index.md` — 关键词→文件索引
- `_knowledge/_index/topic-index.md` — 本文件，主题→文件索引

---

## 4. 错误处理与恢复

### 超时处理
- `_knowledge/_enhancement/subagent-timeout-recovery.md` — 超时预防/恢复/监控
- `_knowledge/knowledge-error-patterns.md` — 错误模式库（来自 debug skill）

### 并行增强
- `_knowledge/_enhancement/parallel-enhancement-batch.md` — 批次规划/监控/完成标准

### 内容处理
- `_knowledge/_enhancement/multilang-content-handling.md` — UTF-8 BOM/LaTeX/表格规则

---

## 5. 财务合规（L 层）

### 内部控制
- `_knowledge/_components/financial-compliance.md` — 内控检查点

### 合规审计
- `_knowledge/_components/financial-compliance.md` — 合规性审查流程

### 审计报告
- `_knowledge/references/audit-report-format.md` — 审计报告格式模板

---

## 6. 行为规则（R1-R5）

| 规则 | 主题 | 映射文件 |
|------|------|---------|
| R1 | 权限与安全 | `_knowledge/_components/behavior-checker.md` |
| R2 | 数据保护 | `_knowledge/_components/behavior-checker.md` |
| R3 | 可追溯性 | `_knowledge/_components/behavior-checker.md` |
| R4 | 变更控制 | `_knowledge/_components/behavior-checker.md` |
| R5 | 贪心检测 | `_knowledge/_components/behavior-checker.md` |

---

## 7. 参考资料

### 外部专家知识
- `_knowledge/references/external/auditor-expert-knowledge.md` — 8 个专家来源

### 报告模板
- `_knowledge/references/audit-report-format.md` — 审计报告格式

### CI/CD 集成
- `_knowledge/references/ci-cd-integration.md` — CI/CD 流水线集成

---

## 8. 工具脚本

### 知识验证
- `_knowledge/scripts/self-improve.py` — 自优化脚本
- `_knowledge/scripts/check_knowledge_insertion.py` — 知识插入验证（来自 debug）

### 审计工具
- `_knowledge/_components/skill-audit-suite/scripts/` — Skill 审计套件脚本

---

## 9. 核心原则

- `_knowledge/core-principles/auditor-principles.md` — P1-P5 核心原则

| 原则 | 主题 |
|------|------|
| P1 | 先读再改（系统诊断前先读取规则） |
| P2 | 不准假装测试通过 |
| P3 | 不准加没要求的功能 |
| P4 | 先简单后复杂 |
| P5 | 不准过度封装 |

---

## 10. 自学习与进化

### 进化引擎
- `SKILL.md` (S5.9) — 进化引擎流程
- `_knowledge/_components/self-improving-integration.md` — 自我改进集成

### 经验沉淀
- `_knowledge/_refined/LEARNINGS.md` — 自学习经验骨架

---

## 11. AI治理框架（新，v1.1）

### NIST AI RMF
- `_knowledge/references/external/auditor-expert-knowledge.md` — 来源9 GenAI Profile (NIST-AI-600-1)
- 四大核心函数：Govern > Map > Measure > Manage
- 风险分级制度 + 审计轨迹要求

### NIST AI RMF Playbook
- `_knowledge/references/external/auditor-expert-knowledge.md` — 来源10 Govern章节
- 风险量化公式 + AI全链路文档要求

### GAO AI Accountability Framework
- `_knowledge/references/external/auditor-expert-knowledge.md` — 来源11 GAO-21-519SP
- 四大原则（Governance/Data/Performance/Monitoring）
- 第三方审计 + 审计问题清单

---

**更新日志**：
- v1.1 (2026-05-22): 追加主题11 AI治理框架（来源9-11），更新外部专家数量 8→12