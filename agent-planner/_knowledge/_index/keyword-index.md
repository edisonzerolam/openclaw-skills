# agent-planner 关键词索引

> 关键词 → 文件映射，≤3行/条目

---

## 规划触发词

| 关键词 | 映射文件 |
|--------|---------|
| 规划 | SKILL.md (P-Sub-P) |
| 方案设计 | SKILL.md (P-Sub-P) |
| Agent架构 | SKILL.md (P-Sub-P) |
| 任务分解 | SKILL.md (P-Sub-P) |
| 规划修正 | SKILL.md (P-Sub-P) |
| 多方案对比 | SKILL.md (P1) |
| 详细设计 | SKILL.md (P2) |
| 执行清单 | SKILL.md (P3) |

## F1-F12核心流程词

| 关键词 | 映射文件 |
|--------|---------|
| 前置验证 | SKILL.md (F1) |
| 用户确认 | SKILL.md (F2) |
| 成本预估 | SKILL.md (F3) |
| 架构方案 | SKILL.md (F4) |
| 技能选型 | SKILL.md (F5) |
| 工作流编排 | SKILL.md (F6) |
| 坑点预警 | SKILL.md (F7) |
| 环境配置 | SKILL.md (F8) |
| Workspace检查 | SKILL.md (F9) |
| 适用场景 | SKILL.md (F10) |
| 子代理调用 | _knowledge/_enhancement/spawn-patterns.md |
| 版本追踪 | _knowledge/_enhancement/plan-tracker/tracker.md |

## 知识库领域词

| 关键词 | 映射文件 |
|--------|---------|
| 医疗器械 | _knowledge/_enhancement/knowledge-base-integration.md |
| 设备/耗材/IVD | _knowledge/_enhancement/knowledge-base-integration.md |
| 投标/标书/中标 | _knowledge/_enhancement/knowledge-base-integration.md |
| 股票/A股/港股 | _knowledge/_enhancement/knowledge-base-integration.md |
| 基金/净值/ETF | _knowledge/_enhancement/knowledge-base-integration.md |
| 理财/资产配置 | _knowledge/_enhancement/knowledge-base-integration.md |
| 知识工程 | _knowledge/_enhancement/knowledge-engineering-pattern.md |
| 蒸馏/专家注入 | _knowledge/_enhancement/knowledge-engineering-pattern.md |

## 坑点库词

| 关键词 | 映射文件 |
|--------|---------|
| 超时 | _knowledge/_enhancement/pitfall-library.md (T1/T7/T12) |
| 编码问题 | _knowledge/_enhancement/pitfall-library.md (T8) |
| 版本混乱 | _knowledge/_enhancement/pitfall-library.md (T11) |
| 子代理隔离 | _knowledge/_enhancement/pitfall-library.md (T4) |
| 未经确认修改 | _knowledge/_enhancement/pitfall-library.md (T7) |
| 需求变更 | _knowledge/_enhancement/pitfall-library.md (T12) |
| 知识工程坑点 | _knowledge/_enhancement/knowledge-pitfall-library.md |
| 插入位置错误 | _knowledge/_enhancement/knowledge-engineering-pattern.md |
| 专家来源虚构 | _knowledge/_enhancement/knowledge-engineering-pattern.md |

## 子代理调用词

| 关键词 | 映射文件 |
|--------|---------|
| agent-team | _knowledge/_enhancement/spawn-patterns.md |
| sessions_spawn | _knowledge/_enhancement/spawn-patterns.md |
| L1/L2/L3 | _knowledge/_enhancement/spawn-patterns.md |
| Task parallel | _knowledge/_enhancement/spawn-patterns.md |
| E6多源并行 | _knowledge/_enhancement/spawn-patterns.md |
| F11子代理 | _knowledge/_enhancement/spawn-patterns.md |

## 版本/追踪词

| 关键词 | 映射文件 |
|--------|---------|
| 版本迭代 | _knowledge/_enhancement/plan-tracker/evolution-log.md |
| 版本号 | SKILL.md (v{主}.{次}) |
| 版本追踪 | _knowledge/_enhancement/plan-tracker/tracker.md |
| 残余变更 | _knowledge/_enhancement/plan-tracker/residual-generator.md |
| Cron生成 | _knowledge/_enhancement/plan-tracker/residual-generator.md |

## Workspace分区词

| 关键词 | 映射文件 |
|--------|---------|
| 4-Zone | _knowledge/_enhancement/workspace-zones.md |
| Zone A/B/C/D | _knowledge/_enhancement/workspace-zones.md |
| Workspace卫生 | _knowledge/_enhancement/workspace-zones.md |

## KANO模型词

| 关键词 | 映射文件 |
|--------|---------|
| M必备型 | SKILL.md (F5) |
| O期望型 | SKILL.md (F5) |
| A魅力型 | SKILL.md (F5) |
| MVP | SKILL.md (F5) |

## 质量自检词

| 关键词 | 映射文件 |
|--------|---------|
| 完整性 | SKILL.md (质量自检) |
| 可执行性 | SKILL.md (质量自检) |
| 风险控制 | SKILL.md (质量自检) |
| Token效率 | SKILL.md (质量自检) |
| 模型调用效率 | SKILL.md (质量自检) |

---

## 规划框架/文献（新，v1.1）

| 关键词 | 映射文件 |
|--------|---------|
| ReAct | _knowledge/references/external/agent-planner-expert-knowledge.md # 来源9 推理-行动交替 |
| MetaGPT | _knowledge/references/external/agent-planner-expert-knowledge.md # 来源10 SOP编码+装配线 |
| LLM Agent规划综述 | _knowledge/references/external/agent-planner-expert-knowledge.md # 来源11 arXiv:2402.02716 |
| AgentBench | _knowledge/references/external/agent-planner-expert-knowledge.md # 来源12 Agent评估Benchmark |
| NeuroMAS | _knowledge/references/external/agent-planner-expert-knowledge.md # 来源13 RL自动协作 |
| BOAD | _knowledge/references/external/agent-planner-expert-knowledge.md # 来源14 Bandit优化 |
| SCOPE | _knowledge/references/external/agent-planner-expert-knowledge.md # 来源15 蒸馏规划能力 |
| Close the Loop | _knowledge/references/external/agent-planner-expert-knowledge.md # 来源16 Role-Playing数据生成 |
| Trustworthy Agentic AI | _knowledge/references/external/agent-planner-expert-knowledge.md # 来源17 多模态安全 |
| 自适应规划深度 | _knowledge/references/external/agent-planner-expert-knowledge.md # 来源18 解决过度规划 |
| 过度规划 | _knowledge/references/external/agent-planner-expert-knowledge.md # 来源18 Self-Regulated Planning |

---

*本文件为 agent-planner skill 的关键词索引，版本 v1.1*
*更新：2026-05-22，追加规划框架/文献关键词*