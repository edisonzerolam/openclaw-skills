# agent-planner 自学习记录

> 本文件记录 agent-planner 的学习进化历程，触发自学习机制时自动更新

---

## 学习触发机制

| 触发条件 | 触发动作 | 更新文件 |
|---------|---------|---------|
| 规划任务完成 | 记录执行摘要到LEARNINGS.md | LEARNINGS.md |
| 新坑点发现 | 新坑点追加到pitfall-library.md | pitfall-library.md |
| 专家知识注入 | 更新expert-knowledge.md | references/external/agent-planner-expert-knowledge.md |
| 新主题发现 | 更新topic-index.md和keyword-index.md | _index/*.md |
| 核心原则修正 | 更新agent-planner-principles.md | core-principles/agent-planner-principles.md |

---

## 执行记录（按时间倒序）

### 2026-06-03 02:47
**触发任务**: 技能优化方案 v2.0 执行
**执行动作**: 新增 F0.5 事实验证子阶段，集成 fact_check.py，补充阻塞规则
**学习成果**: 规划产物中的数字必须现场验证（fact_check.verify_source_claims），不能依赖历史报告。FAIL 阻塞 F1，WARN 用户决策。
**更新文件**: SKILL.md（F0.5）、frozen_version.json（v3.4）

---

## 坑点积累（按发现时间正序）

| 日期 | 坑点编号 | 坑点描述 | 来源任务 |
|------|---------|---------|---------|
| 2026-06-03 | T13 | 规划数字与实际不符（行数+14%、文件大小+98%） | auditor LEARNINGS 多源报告偏差案例 |
| 2026-06-03 | T14 | 子代理接受二手数据未独立验证 | auditor LEARNINGS 多源报告偏差案例 |
| 2026-06-03 | T15 | 多版本迭代无收敛标准 | T6 补充（5版上限未执行） |

---

## 专家知识积累

| 日期 | 来源专家 | 核心概念 | 引用文件 |
|------|---------|---------|---------|
| 2026-06-03 | auditor LEARNINGS | 多源报告数字偏差必须现场验证 | auditor/_knowledge/_refined/LEARNINGS.md |

---

## 版本演进

| 版本 | 日期 | 变更摘要 |
|------|------|---------|
| v1.0 | 2026-05-22 | 初始骨架建立，8个专家知识来源 |
| v1.1 | 2026-06-03 | 激活首批学习记录：F0.5验证机制 + T13/T14/T15坑点 |

---

*本文件为 agent-planner skill 的自学习记录，版本 v1.1*
*更新规则：触发自学习机制时追加，禁止删除历史记录*
