---
name: agent-planner
description: "Agent 规划修正技能。用于 auditor 的 P-Sub-P 阶段，提供 P1/P2/P3 级规划。触发词：「规划」「方案设计」「Agent 架构」「任务分解」。不适用：纯信息查询、单步执行指令。"
---

## 需求路由

```python
def route_demand(demand: str) -> str:
    d = demand.lower()
    if any(kw in d for kw in ["派生子代理", "spawn", "执行审查"]): return "local"
    if any(kw in d for kw in ["规划", "方案设计", "帮我生成"]): return "llm"
    if any(kw in d for kw in ["坑点", "风险"]): return "hybrid"
    if any(kw in d for kw in ["检索", "知识库"]): return "hybrid"
    return "llm"
```

| 模式 | 说明 |
|------|------|
| local | 子代理派发、知识缓存、索引更新 |
| llm | 规划方案生成、Agent 架构设计 |
| hybrid | 本地优先 → 置信度<70% 时 fallback 到 LLM |

## 执行流程

### F0 — 调查（强制入口）

任何规划任务必须先完成调查，产出调查摘要，再进入 F1。

**调查维度**：事实 / 范围 / 深度 / 依赖 / 风险 / 资源

**调查摘要格式**：
```markdown
## 调查摘要
- 事实：{现有条件概述}
- 范围：{规划边界}
- 复杂度：{简单/中等/复杂 + 依据}
- 主要依赖：{依赖项}
- 风险点：{风险}
- 资源约束：{时间/Token/预算}
```

### F0.5 — 事实验证（强制）

调查摘要产出后、进入 F1 前，必须对关键数字声明执行现场验证。

**验证维度**：文件行数 / 文件大小 / 路径存在性 / API 签名 / 版本号 / 文件数量

```python
from fact_check import verify_source_claims
verifications = verify_source_claims(source_claims, base_dir=".")
```

**结果判定**：
| 结果 | 条件 | 动作 |
|------|------|------|
| PASS | 所有验证通过，偏差<10% | 放行 → F1 |
| WARN | 偏差 10%-30% | 标记待核实, 用户决策 |
| FAIL | 偏差>30% 或文件不存在 | 阻塞, 修正后重试 |

验证结果写入调查摘要的 `verification_results` 字段。

### F1 — 前置验证
- rules.md + identity-config.md 存在 → 否：阻塞
- 核心 skill 已安装 → 否：降级到通用能力
- 变更目标可确认 → 否：追问确认

### F2 — 用户确认
- 规划方案输出后等待用户确认
- 修改型变更（≥P1）需显式确认

### F3 — 成本预估
| 指标 | 预估方式 |
|------|---------|
| Token 消耗 | 简单≤5K / 中等≤20K / 复杂≤50K |
| 模型调用次数 | Task 数 × 1.2（含重试）|
| 迭代上限 | 5 版，超限强制用户决策 |

### F4-F12 — 详细规划流程

详细流程（F4 架构方案 → F12 残余 Cron 生成）见 `references/workflow.md`。

| 步骤 | 概要 |
|------|------|
| **F4 架构方案** | Agent 组成 / rules.md / identity-config.md / 通信 / 降级 |
| **F5 技能选型** | KANO 模型：M(必备)/O(期望)/A(魅力)，MVP 只含 M |
| **F6 工作流编排** | Epic→Task→Step 三级分解，含并行标记 |
| **F7 坑点预警** | 读取坑点库 + 外部经验，≥3 个匹配坑点 |
| **F8 环境配置** | 依赖清单 + 验证命令 + 安装方式 |
| **F9 Workspace 卫生** | 4-Zone 模型检查 |
| **F10 适用场景** | 明确适用/不适用边界 |
| **F11 子代理调用** | 3 级执行路径（L1-L3） |
| **F12 交付追踪** | T1-T5 版本追踪 + 残余 Cron 生成 |

### 阶段A — 审计（强制）

规划方案完成后、用户确认前必须执行审计。见 `references/audit-protocol.md`。

| 维度 | 通过标准 |
|------|---------|
| 完整性 | 质量维度全部≥3/5 |
| 准确性 | 无虚假/夸大描述，数字经 F0.5 验证 |
| 一致性 | 与调查摘要/rules.md 一致 |
| 可执行性 | Task 依赖/步骤清晰 |
| 风险控制 | 坑点≥3 个且降级策略完整 |

## 知识库检索

规划涉及特定领域时检索知识库。详见 `_knowledge/_enhancement/knowledge-base-integration.md`。

| 关键词 | 目录 | 优先级 |
|--------|------|:------:|
| 医疗器械/投标 | medical-device, bidding | P0 |
| 股票/A股/港股 | stock | P1 |
| 基金/ETF | fund | P1 |
| 理财/资产配置 | finance | P1 |

## 质量自检

| 维度 | 评分 |
|------|:----:|
| 完整性 | X/5 |
| 可执行性 | X/5 |
| 风险控制 | X/5 |
| Token 效率 | X/5 |
| 模型调用效率 | X/5 |

综合≥3.5 → 通过；<3.0 → 需改进

## 版本迭代
- 迭代上限 5 版，超限强制用户决策
- 版本号格式：`v{主}.{次}`
- 每版记录变更摘要到 `_knowledge/_enhancement/plan-tracker/evolution-log.md`

## 分级加载索引

| 层级 | 文件 | 加载时机 |
|------|------|---------|
| **L1** | SKILL.md（核心+F0-F3） | 首次加载 |
| **L2** | `references/workflow.md`, `references/audit-protocol.md` | SKILL.md 后自动 |
| **L2** | `_knowledge/_enhancement/knowledge-engineering-pattern.md` | SKILL.md 后自动 |
| **L3** | `_knowledge/_enhancement/knowledge-base-integration.md` | 知识库检索关键词命中 |
| **L3** | `_knowledge/_enhancement/plan-tracker/*.md` | F12 版本追踪触发 |
| **L3** | `_knowledge/_enhancement/pitfall-library.md` | F7 坑点预警触发 |
| **L4** | `_knowledge/_enhancement/plan-template.md` | 规划文档输出 |
| **L4** | `_knowledge/_enhancement/spawn-patterns.md` | F11 spawn 调用 |
| **L4** | `_knowledge/_enhancement/workspace-zones.md` | F9 workspace 检查 |

## 自学习 & 事实核查

**事实核查**：每次执行完成、返回结果前，必须调用 `_shared/fact-checker/fact_check.py`。
详见 `references/self-learning.md`。

## 参考文件

| 文件 | 用途 |
|------|------|
| `references/workflow.md` | F4-F12 详细流程 |
| `references/audit-protocol.md` | 阶段A 审计 + 质量自检 |
| `references/self-learning.md` | 自学习 + 事实核查 + 优化模块 |
| `_knowledge/_enhancement/plan-template.md` | 规划方案模板 |
| `_knowledge/_enhancement/pitfall-library.md` | 坑点库 v1.1（12 坑）|
| `_knowledge/_enhancement/spawn-patterns.md` | F11/E6 子代理调用模式 |
| `_knowledge/_enhancement/workspace-zones.md` | 4-Zone Workspace 分区 |
| `_knowledge/_enhancement/knowledge-base-integration.md` | 知识库检索 |
| `_knowledge/_enhancement/plan-tracker/` | 版本追踪 + 残余 Cron |
| `_knowledge/_enhancement/expert-distillation-flow.md` | 蒸馏/专家注入 |
| `_knowledge/_refined/LEARNINGS.md` | 经验精化记录 |
| `_knowledge/_index/` | 关键词/主题索引 |
| `_knowledge/core-principles/` | 核心原则 |
| `references/plan-tracker-deprecated.md` | 旧版追踪（已弃用）|

## 故障与降级

| 场景 | 处理 |
|------|------|
| fact_check.py 不可达 | 回退到 exec 命令验证 |
| 子代理全部超时 | 强制降级主会话执行 |
| 知识缓存 I/O 失败 | 跳过缓存，直接读取文件 |
| F0.5 验证 FAIL | 阻塞，通知用户修正后重试 |
| 审计迭代超 5 版 | 强制用户决策 |