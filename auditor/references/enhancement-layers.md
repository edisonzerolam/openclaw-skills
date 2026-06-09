# auditor 增强层 A-N 矩阵

| 层 | Skill/来源 | 嵌入点 | 触发关键词 |
|:--:|-----------|:------:|-----------|
| A | skill-audit-suite (CI/CD) | S1 | ci/cd, pipeline, github, git |
| B | behavior-institutionalization | Q6 | 合规, r1-r5, 行为红线 |
| C | skill-context-hygiene | Q0 | context, 上下文, 内存 |
| D | skill-session-manager | S2/S4 | 子会话, subagent, session |
| E | agent-planner | P-Sub-P | 规划, 方案设计, 架构 |
| F | deep-research | S1 | 调研, research, 研究 |
| G | self-improving + capability-evolver | S5 | 进化, 学习, 自改进 |
| H | sessions_spawn + agent-team（运维）| S2/S4 | 子 Agent 派发/团队协作 |
| I | docx/pptx | S5 | 报告, 文档输出 |
| J | knowledge-base | S1/S5 | 知识库, 领域知识 |
| K | s1-quality-attributes | S1 | 质量, 多线索, Token |
| L | 财务合规审计（内控）| S1/S3/S5 | 财务, 审计, 内控, 合规 |
| M | 多源报告核查 | S1/S3 | 专家小组, 多报告, second opinion |
| N | Expert Panel Protocol | S2/S3 | 专家小组, 4 角色, 安全专家 |

> ⚠️ **Windows+WSL 限制**：agent-team spawn subprocess 0/6 成功率，H 层派发全部用 sessions_spawn。agent-team 仅限 WSL 内运维命令（team list/sync）。

### 层优先级

| 级别 | 含义 |
|:----:|------|
| L2 | SKILL.md 后自动加载（热数据）|
| L3 | 触发词命中后按需加载（冷数据）|
| L4 | 专家模式或 S5.9 进化引擎触发 |