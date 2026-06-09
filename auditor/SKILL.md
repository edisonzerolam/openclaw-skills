---
name: auditor
description: "系统优化审计 + 财务合规审计。强触发词：「审计」「优化建议」「变更审查」「系统诊断」「合规检查」「内部控制」「财务合规」。不适用：单文件格式检查、简单提问、非变更类操作。"
---

## 需求路由

```python
def route_demand(demand: str) -> str:
    d = demand.lower()
    if any(kw in d for kw in ["质量检查", "q0", "版本锁定"]): return "local"
    if any(kw in d for kw in ["审计报告", "帮我生成"]): return "llm"
    if any(kw in d for kw in ["审计风险", "合规判断"]): return "hybrid"
    return "llm"
```

| 模式 | 说明 |
|------|------|
| local | Q0-Q7 并行质量检查、版本锁定、依赖缺口 |
| llm | 审计报告生成、合规判断、增强层选择 |
| hybrid | 本地检查 + LLM 评估 |

## 阶段0 — 调查（强制入口）

任何审计任务必须先完成调查，产出调查摘要，再进入 Phase-G。

| 维度 | 内容 | 产出 |
|------|------|------|
| 事实 | 现状/已有文件/配置 | 事实清单 |
| 范围 | 审计边界 | 范围文档 |
| 深度 | 简单/中等/复杂 | 复杂度评级 |
| 依赖 | 外部依赖可用性 | 依赖矩阵 |
| 风险 | 历史失败案例 | 风险清单 |
| 资源 | Token/时间预算 | 资源约束 |

**调查方法**：workspace 扫描 + rules.md/identity-config.md 读取 + `memory_search` + sessions_spawn 测试依赖

**调查摘要格式**：
```markdown
## 调查摘要
- 事实：{现状}
- 范围：{边界}
- 复杂度：{简单/中等/复杂 + 依据}
- 主要依赖：{依赖项}
- 风险点：{风险}
- 资源约束：{时间/Token/预算}
```

## Phase-G — 目标分类（强制，5 步）

| 步骤 | 输出 | 要点 |
|------|------|------|
| G1 变更分类 | classification | Agent/Skill/系统/跨Agent/进行中/回滚/**财务合规** |
| G2 核心问题 | core_problem | 一句话描述 + 目标 |
| G3 成功标准 | success_criteria | 可验证指标 |
| G4 范围确认 | scope | 影响范围 + 边界 + 交叉影响 |
| G5 增强层过滤 | translated_change | A-N 14层自动甄别；confidence≥0.6 升级 |

**增强层 A-N** 详见 `references/enhancement-layers.md`。

## Layer0 — 质量门槛（前置必做）

| 检查 | 要点 | 参考 |
|------|------|------|
| Q0 Context 健康 | 3 维度检查 | `_knowledge/_components/context-hygiene.md` |
| Q1 依赖缺口 | 增强层 A-L 是否遗漏 | — |
| Q2 确认类型 | 是否需要用户确认 | — |
| Q3 复杂度 | 变更是否>5 个 | — |
| Q4 版本锁定 | 版本是否锁定 | frozen_version.json |
| Q5 子代理关联 | workspace 关联正确性 | — |
| Q6 行为红线 | R1-R5 检查 | `_knowledge/_components/behavior-checker.md` |
| Q7 修复对象就绪 | 单一文件/代码/配置类审计？ | 决定是否可输出修复对象 |

## Phase-S — 执行框架（概要）

详见 `references/execution-framework.md`。

| 阶段 | 概要 |
|------|------|
| **S1 战略评估** | 8 项准考察 + 风险评级 L1-L4 + 质量属性 QA1-QA5 + 财务合规层（如适用）|
| **S2 规划合并** | JSON 规划文档 + 子代理分发 |
| **S3 合并审核** | S3a 预检 → S3b Merge Gate → **S3c Review Loop（3 次迭代）** |
| **S4 执行验证** | E5 备份 + 8 项验证 → **S4.5 代码实读验证（强制）** |
| **S5 结果归档** | Artifact 输出 + S5.5 循环限制 → S5.9 进化 → S5.10 经验写入 → S5.11 修复对象输出 |

### S3c Review Loop 核心

S3b 发现 P0/P1 fail 时触发，限 3 次迭代（R0/R1/R2）。

```
S3c.1 收集 fail → S3c.2 派发子代理修复 → [SG1门禁] → S3c.3 验证修复
→ S3c.4 回归 S3b → [SG2门禁] → 通过→S5，未通过→迭代+1
```

**SG1 门禁**（S3c.2→S3c.3）：成功率≥60% + P0 清零 + P1 修复率≥80%
**SG2 门禁**（S3c.4→S5）：无新 P0 + 新 P1≤3 + 有 justification

详见 `_knowledge/_components/s3c-review-loop-protocol.md`。

## R1-R5 行为红线（强制）

| 规则 | 简写 | 默认 |
|:----:|------|:----:|
| R1 | 不加不需要的功能 | block |
| R2 | 不过度封装 | warn |
| R3 | 不破坏测试 | block |
| R4 | 不假装测试通过 | block |
| R5 | 先读再改 | warn |

## 阶段A — 审计（强制）

审计方案完成后、实施前必须执行。详见 `references/audit-protocol.md`。

| 维度 | 通过标准 |
|------|---------|
| 完整性 | Phase-G + S1-S5 齐全，≥3/5 |
| 准确性 | 无虚假描述 |
| 一致性 | 与调查摘要一致 |
| 可执行性 | Task 依赖/步骤清晰 |
| 风险控制 | 风险评级合理 + 降级策略完整 |

## Phase-D — 风险评估（可选）

变更步骤>5 时触发：D1 范围 → D2 原因 → D3 缓解 → D4 失效代价

## Layer2 — 版本锁定

- 版本文件：`frozen_version.json`
- 解锁条件：连续 3 次 clean 审计
- 锁定时禁止 P-Sub-P 修改

## 分级加载索引

| 层级 | 文件 | 加载时机 |
|------|------|---------|
| **L1** | SKILL.md（核心+Phase-G+Layer0） | 首次加载 |
| **L2** | `references/execution-framework.md`, `references/audit-protocol.md` | SKILL.md 后自动 |
| **L2** | `_knowledge/_components/context-hygiene.md` | C 层 (Q0) |
| **L2** | `_knowledge/_components/behavior-checker.md` | B 层 (Q6) |
| **L2** | `_knowledge/_components/s1-quality-attributes.md` | K 层 |
| **L2** | `_knowledge/_components/financial-compliance.md` | L 层（财务合规）|
| **L3** | `_knowledge/_enhancement/subagent-timeout-recovery.md` | 超时/恢复 |
| **L3** | `_knowledge/_components/s3c-review-loop-protocol.md` | S3c 触发 |
| **L4** | `_knowledge/_components/skill-audit-suite/SKILL.md` | skill 审计 |
| **L4** | `_knowledge/enhancement-registry.md` | 专家模式 |

## 参考文件

| 文件 | 用途 |
|------|------|
| `references/execution-framework.md` | S1-S5 详细执行框架 |
| `references/audit-protocol.md` | 阶段A 审计协议 |
| `references/enhancement-layers.md` | A-N 14 层增强层明细 |
| `references/self-learning.md` | 自学习 + 事实核查 + 优化模块 |
| `_knowledge/_components/` | 各层组件详见知识库 |
| `_knowledge/_enhancement/` | 增强层知识注入 |

## 故障与降级

| 场景 | 处理 |
|------|------|
| 子代理全部超时 | 强制降级主会话（mandatory_override=true）|
| fact_check.py 不可达 | 回退到 exec 验证 |
| SG1 成功率<60% | 主会话接管 + 继续执行 |
| 审计迭代超 5 版 | 强制用户决策 |
| 代码验证 FAIL（S4.5）| 修正结论后重新评分，严禁未验证输出 |