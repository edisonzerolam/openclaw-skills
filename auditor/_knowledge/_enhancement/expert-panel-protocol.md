# Expert Panel Protocol — Layer N

> 版本：v1.1 | 状态：active
> 来源：auditor v6.7 改进（P2-2 Expert Panel 触发过于宽松）
> 依赖：SKILL.md Phase-S S2 + `session-manager.md`

---

## 概述

Layer N Expert Panel 是 S2 Parallel 模式的角色增强版。当 T3+ 任务触发 Expert Panel 时，从 4 个专业角色视角并行审查，提供更全面的审计覆盖。

**与 S2 Parallel 的区别**：

| 维度 | S2 Parallel | Layer N Expert Panel |
|------|------------|---------------------|
| 角色 | 无专业角色 | 4 个专业角色 |
| 审查视角 | 通用规划 | 安全 + 可靠性 + 集成 + 架构 |
| 适用场景 | T1-T2 简单任务 | T3+ 复杂任务 |

---

## N1 — 角色定义

| 角色 | 职责 | 触发关键词 |
|------|------|-----------|
| **安全专家** | 安全漏洞、认证授权、HMAC、token、会话劫持 | 安全/漏洞/认证/HMAC/token |
| **可靠性专家** | 超时恢复、失败路径、异常处理、资源泄漏 | 超时/恢复/失败/异常/资源 |
| **集成专家** | 子代理协调、sessions_spawn、跨Agent协议 | 子代理/会话/session/协调 |
| **架构专家** | 系统变更、配置变更、Gateway/Config结构 | 架构/配置/Gateway/config |

---

## N2 — 触发条件（v1.1 优化）

**v1.0 原问题**：`complexity >= 3` 即触发 4 个专家，可能产生不必要开销。

**v1.1 优化**：增加 queue 项数量 + P0 存在两个二次判断维度，补充 token 预算感知。

```python
def should_trigger_expert_panel(phase_g, complexity, queue_items, audit_findings, token_budget_ratio=1.0):
    """
    判断是否触发 Expert Panel（4角色专家小组）
    
    参数：
      phase_g: Phase-G 分类结果
      complexity: 复杂度等级 T1-T5
      queue_items: queue 项数量
      audit_findings: 审计发现列表
      token_budget_ratio: 可用 token 预算比例（0.0-1.0），低于 0.3 时自动降级
    
    返回：('expert_panel', reasoning) 或 ('s2_parallel', reasoning)
    """
    # ── 降级条件（优先判断，满足任一即降级）─────────────────
    if token_budget_ratio < 0.3:
        return ('s2_parallel', 'token_budget_low')
    if queue_items < 3:
        return ('s2_parallel', 'queue_items_too_small')
    
    # ── 核心触发条件 ──────────────────────────────────────
    if complexity >= 3 and queue_items >= 5:
        # P0 存在 → 安全性优先，强制触发（即使 token 紧张）
        if any(f.get('severity') == 'P0' for f in audit_findings):
            return ('expert_panel', 'p0_found')
        
        # G1 分类为高风险类型
        if phase_g.classification in ["系统变更", "跨Agent协议"]:
            return ('expert_panel', 'high_risk_classification')
        
        # 安全敏感关键词命中
        security_keywords = ["安全", "漏洞", "认证", "授权", "HMAC", "token"]
        if any(kw in phase_g.core_problem for kw in security_keywords):
            return ('expert_panel', 'security_keyword_hit')
    
    # 默认降级为 S2 Parallel
    return ('s2_parallel', 'trigger_conditions_not_met')
```

**决策树**：

```
[token_budget_ratio < 0.3] ──→ ❌ 降级 S2 Parallel（token_budget_low）
          ↓ False
[queue_items < 3] ──────────→ ❌ 降级 S2 Parallel（queue_items_too_small）
          ↓ False
[complexity >= 3 AND queue_items >= 5]
          │
          ├── [存在 P0] ─────────→ ✅ Expert Panel（p0_found）
          ├── [G1 in 高风险类] ──→ ✅ Expert Panel（high_risk_classification）
          ├── [命中安全关键词] ──→ ✅ Expert Panel（security_keyword_hit）
          └── 以上均不满足 ─────→ ❌ 降级 S2 Parallel
```

---

## N2.5 — 降级路径（v1.1 新增）

### 降级触发条件

满足以下任一条件时，主会话可决定降级为 S2 Parallel 模式：

| 条件 | 阈值 | 说明 |
|------|------|------|
| token 预算不足 | `token_budget_ratio < 0.3` | 可用预算低于 30% |
| queue 规模太小 | `queue_items < 3` | 问题太少不值得 4 专家 |
| 主会话判定开销过大 | `main_session_overhead == True` | 主会话显式标记 |

### 降级 checkpoint 记录要求

降级发生时，必须在 checkpoint 文件中记录：

```python
# checkpoint 降级记录格式
{
    "event": "expert_panel_degraded",
    "degraded_at": "<ISO8601>",
    "reason": "<token_budget_low | queue_items_too_small | overhead_decision>",
    "fallback_mode": "s2_parallel",
    "original_complexity": "<T3-T5>",
    "queue_items_at_degrade": <int>,
    "token_budget_ratio_at_degrade": <float>,
    "notification_sent": True  # 主会话已通知
}
```

**路径**：`~/.qclaw/skills/auditor/_checkpoints/`
**命名**：`degrade_{timestamp}.json`

### 降级通知主会话

降级后，主会话收到子代理 completion event 时，应报告：
- 降级原因（不含敏感 token 数据）
- fallback 到 S2 Parallel 的并行能力保留情况
- 关键建议（如 token 预算低则建议用户追加预算）

### S2 Parallel 模式保留能力

降级为 S2 Parallel 后，仍保留以下能力：
- 并行派发子代理（`sessions_spawn`，最多 3 个并发）
- checkpoint 写入
- S3c Review Loop 触发
- 质量门禁（SG1/SG2）

**不保留**：4 角色专业视角审查（安全/可靠性/集成/架构各 1 专家）

---

## N3 — 工作分工

| 角色 | 审查内容 | 输出 |
|------|---------|------|
| **安全专家** | 安全漏洞、认证授权、HMAC、token | `FINDING-SEC-XXX` |
| **可靠性专家** | 超时恢复、失败路径、异常处理 | `FINDING-REL-XXX` |
| **集成专家** | 子代理协调、sessions_spawn、跨Agent协议 | `FINDING-INT-XXX` |
| **架构专家** | 系统变更、配置变更、Gateway/Config结构 | `FINDING-ARC-XXX` |

---

## N4 — 结果汇总

```python
expert_panel_report = {
    "triggered": True,
    "mode": "expert_panel",  # v1.1 新增：区分 expert_panel / s2_parallel
    "degraded": False,        # v1.1 新增：降级标记
    "degrade_reason": None,   # v1.1 新增：降级原因
    "iteration": "R0",
    "roles": {
        "security": {"findings": [...], "status": "PASSED"},
        "reliability": {"findings": [...], "status": "PASSED"},
        "integration": {"findings": [...], "status": "FAILED"},  # 发现问题
        "architecture": {"findings": [...], "status": "PASSED"}
    },
    "summary": {
        "total_findings": 3,
        "by_severity": {"P0": 0, "P1": 2, "P2": 1},
        "blocking_findings": 1  # integration 发现问题，阻塞
    }
}
```

**汇总判定**：
- 任一角色发现 P0 → 整体评级提升至 P0
- 任一角色发现 P1 且无对应修复 → 进入 S3c Review Loop
- 全部角色通过 → 进入 S5 归档

**S2 Parallel 降级模式汇总格式**：

```python
s2_parallel_report = {
    "triggered": False,
    "mode": "s2_parallel",
    "degraded": True,
    "degrade_reason": "<token_budget_low | queue_items_too_small | overhead_decision>",
    "fallback_roles": None,  # 无专业角色，但仍执行通用并行审查
    "summary": {
        "total_findings": <int>,
        "by_severity": {"P0": 0, "P1": <int>, "P2": <int>},
        "blocking_findings": <int>
    }
}
```

---

## N5 — Expert Panel 与 S3c Review Loop 协作

```
Phase-S 执行框架（局部）
    │
    ├── S2 规划合并
    │     └── [N2 触发判断]
    │           ├── 触发 Expert Panel → 4角色并行审查 → N4汇总
    │           │                                     ↓
    │           │                              [发现 P0/P1]
    │           │                                     ↓
    │           └── 降级 S2 Parallel → 并行通用审查 → N4汇总(s2_parallel)
    │                                              ↓
    ├── S3 Merge Gate
    │     └── 发现 fail 项 → S3c Review Loop
    │
    └── S3c Review Loop
              └── [N4 汇总结果] 可作为 S3c.1 的输入补充
```

Expert Panel 的 `expert_panel_report` 或 S2 Parallel 的 `s2_parallel_report` 可并入 `audit_review_queue`，作为 S3c.1 的输入补充。

---

## N6 — S2 Parallel 模式定义（v1.1 新增）

> **来源**：session-manager.md 中 S2 Parallel 模式的正式定义补全
> **定位**：S2 规划阶段的轻量并行模式，作为 Expert Panel 的降级路径

### 触发条件

满足以下任一即以 S2 Parallel 模式执行：
1. N2 决策返回 `('s2_parallel', reason)`
2. 主会话主动降级（开销判定）
3. queue_items < 3（规模太小）

### 行为定义

| 行为 | S2 Parallel 模式 | 说明 |
|------|----------------|------|
| 子代理派发 | `sessions_spawn`（最多 3 并发） | 并行执行子任务 |
| 角色分配 | 通用任务分配，无专业角色 | 简化开销 |
| 结果汇总 | 主会话合并（无 N4 专业分类） | 主会话负责 |
| checkpoint | 写入 base checkpoint | 同 session-manager.md |
| S3c 协作 | 可触发 S3c Review Loop | 同 Expert Panel |

### 与 Expert Panel 的完整决策流程

```
[任务进入 S2]
      ↓
[N2 should_trigger_expert_panel]
      │
      ├── ('expert_panel', _) ──→ 派发 4 专业角色
      │                              │
      │                         N4 汇总 → S3b/S3c
      │
      └── ('s2_parallel', reason) ──→ S2 Parallel 模式
                                        │
                                   [结果合并]
                                        │
                                   S3b/S3c
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-30 | 初始版本（基于 v3.1 synthesis）|
| **v1.1** | **2026-05-30** | **P2-2优化：N2增加token预算感知；新增N2.5降级路径+checkpoint格式；新增N6 S2 Parallel定义；返回值从bool改为tuple并区分模式** |