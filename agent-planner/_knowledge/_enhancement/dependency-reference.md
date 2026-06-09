# 增强层引用说明

本目录为 agent-planner 增强层引用目录，实际内容指向已安装的外部 Skills：

| 增强层 | Skill | 位置 | 用途 |
|--------|-------|------|------|
| F | deep-research | `~/.agents/skills/deep-research/` | Tier-1 架构方案调研增强 |
| E | agent-planner (self) | `~/.agents/skills/agent-planner/` | P-Sub-P 修复规划 |
| 6e | capability-evolver | `~/.agents/skills/capability-evolver/` | 规划后自我进化（必选增强） |
| Tier-3 | agent-team-orchestration | `~/.agents/skills/agent-team-orchestration/` | 多Agent团队编排（降级为附录参考） |
| Tier-3 | skill-template-generator | `~/.agents/skills/skill-template-generator/` | 技能开发指南 |
| - | skill-prompt-templates | `~/.agents/skills/skill-prompt-templates/` | 5-layer Prompt架构（参考引用） |
| - | knowledge-base | `~/.agents/skills/knowledge-base/` | 需创建（与 auditor 共用） |

> 注意：capability-evolver 在 agent-planner 6e 中为**必选增强**（从可选升为必选）
