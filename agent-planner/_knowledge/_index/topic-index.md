# agent-planner 主题索引

> 主题 → 文件映射，≤3行/条目

---

## 核心主题

### 规划与修正
- **P-Sub-P规划修正**: SKILL.md (P-Sub-P段落) — 3级输出P1/P2/P3
- **F1前置验证**: SKILL.md (F1段落) — Workspace结构/依赖Skill/用户意图
- **F2用户确认**: SKILL.md (F2段落) — 规划方案确认门
- **F3成本预估**: SKILL.md (F3段落) — Token/调用次数/迭代次数
- **F4架构方案**: SKILL.md (F4段落) + _enhancement/plan-template.md
- **F6工作流编排**: SKILL.md (F6段落) — Epic→Task→Step三级分解

### 版本与追踪
- **版本迭代控制**: SKILL.md (版本迭代控制段落) — 5版上限/v{主}.{次}格式
- **计划追踪核心逻辑**: _knowledge/_enhancement/plan-tracker/tracker.md (T1-T5)
- **残余变更Cron生成**: _knowledge/_enhancement/plan-tracker/residual-generator.md
- **跨规划演进记录**: _knowledge/_enhancement/plan-tracker/evolution-log.md

### 子代理与并行
- **F11子代理调用**: _knowledge/_enhancement/spawn-patterns.md — L1/L2/L3三级
- **E6多源并行**: _knowledge/_enhancement/spawn-patterns.md — ≥3来源并行
- **agent-team团队协作**: _knowledge/_enhancement/spawn-patterns.md — 4.4x加速

### 质量与风险
- **质量自检**: SKILL.md (质量自检段落) — 5维度综合≥3.5通过
- **坑点预警**: _knowledge/_enhancement/pitfall-library.md — T1-T12
- **知识工程坑点**: _knowledge/_enhancement/knowledge-pitfall-library.md

## 知识管理主题

### 知识工程
- **知识工程规划模式**: _knowledge/_enhancement/knowledge-engineering-pattern.md
- **专家蒸馏流程**: _knowledge/_enhancement/expert-distillation-flow.md
- **专家来源格式**: _knowledge/_enhancement/knowledge-engineering-pattern.md (4.3节)
- **知识库检索**: _knowledge/_enhancement/knowledge-base-integration.md (F4增强)

### Workspace管理
- **4-Zone分区模型**: _knowledge/_enhancement/workspace-zones.md
- **Workspace卫生检查**: _knowledge/_enhancement/workspace-zones.md (F9)
- **Zone A活跃区**: _knowledge/_enhancement/workspace-zones.md
- **Zone C归档区**: _knowledge/_enhancement/workspace-zones.md

## 技能设计主题

### 技能选型
- **KANO模型**: SKILL.md (F5段落) — M/O/A三级优先级
- **MVP规划**: SKILL.md (F5段落) — 只含M类必备型
- **技能降级策略**: SKILL.md (F1段落) — 核心skill不可用时降级

### 增强层索引
- **L1核心层**: SKILL.md — 首次加载必须
- **L2热数据**: _knowledge/_enhancement/ — 知识工程/坑点库
- **L3冷数据**: _knowledge/_enhancement/ — plan-template/pitfall/spawn/workspace
- **L4专家层**: _knowledge/_enhancement/ — knowledge-base/plan-tracker

## 参考主题

### 模板与工具
- **规划方案模板**: _knowledge/templates/s5-report.md
- **计划追踪初始化**: _knowledge/scripts/plan-tracker-init.py
- **残余生成器**: _knowledge/scripts/residual-generator.py
- **子代理生成器**: _knowledge/scripts/spawn-agent.py

### 外部参考
- **旧版追踪**: references/plan-tracker-deprecated.md
- **CI/CD集成**: references/ci-cd-integration.md

---

## 规划框架研究（新，v1.1）

- **ReAct/推理-行动交替**: `_knowledge/references/external/agent-planner-expert-knowledge.md` # 来源9-11
- **MetaGPT/SOP编码**: `_knowledge/references/external/agent-planner-expert-knowledge.md` # 来源10
- **LLM Agent规划综述**: `_knowledge/references/external/agent-planner-expert-knowledge.md` # 来源11 arXiv:2402.02716
- **2025-2026年前沿**: `_knowledge/references/external/agent-planner-expert-knowledge.md` # 来源13-18

---

*本文件为 agent-planner skill 的主题索引，版本 v1.1*
*更新：2026-05-22，追加规划框架研究方向*