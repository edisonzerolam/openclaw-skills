# S3c Review Loop 协议

> 版本：v1.0 | 状态：active
> 来源：auditor v3.1 改进1（S3c Review Loop）
> 定位：S3b Merge Gate 发现 fail 项后的迭代式复审机制
> 依赖：SKILL.md Phase-S S3b + 超时恢复 `_enhancement/subagent-timeout-recovery.md`

---

## 概述

S3c Review Loop 是 S3 Merge Gate 的迭代子步骤，嵌入在 S3b 之后。当 S3b 发现"核心 fail"项（P0/P1，非 Q6 警告项）时触发。

**与 S2 Parallel 的区别**：
- S2 Parallel：规划阶段的任务分割（多个子代理并行规划）
- S3c Review Loop：修复阶段的迭代式复审（修复 → 回归验证 → 可能再修复）

---

## 触发与退出条件

| 条件类型 | 规则 |
|---------|------|
| **触发** | S3b Merge Gate 发现"核心 fail"项（P0/P1，非 Q6 警告项）|
| **退出（成功）** | `audit_review_queue.stats.pending = 0` + **SG2 通过** |
| **退出（超限）** | R0 → R1 → R2（共3次迭代），超限后记录警告，主会话接管 |
| **安全阀** | 迭代超限后不自动继续，必须主会话显式放行/上报用户 |

---

## 完整流程

```
Phase-S 执行框架（局部）
    │
    ├── S3b Merge Gate（S4后）
    │     ├── 通过 → 进入 S5 归档
    │     └── 发现"核心 fail"项（P0/P1）
    │           │
    │           ▼
    └── S3c Review Loop（限3次迭代 R0/R1/R2）
              │
              ├── [迭代计数检查]
              │     ├── 已达 R2 超限 → 记录警告 + 主会话决策
              │     └── 未达上限 → 继续
              │
              ├── S3c.1：收集 S3b 发现的 fail 项到 audit_review_queue
              ├── S3c.2：按 queue 项内容派发子代理修复
              │          → [SG1 门禁] 子代理全部完成后执行 SG1 检查
              │          → SG1 通过后进入 S3c.3
              ├── S3c.3：验证修复充分性（每项逐一检查修复报告+修复文件）
              ├── S3c.4：回归 S3b Merge Gate（仅重审 queue 项对应的 S4 结果）
              │          → [SG2 门禁] 执行 SG2 检查
              │          → SG2 通过 → queue 清空 → 进入 S5 归档
              │          → SG2 未通过 → 迭代+1，跳转 S3c.1
              └── [checkpoint 写入] S3c.4 后 + 全部超时 + sessions_yield 前
```

---

## audit_review_queue 数据结构

```python
audit_review_queue = {
    "iteration": "R0",                    # R0/R1/R2
    "queue": [
        {
            "id": "FINDING-001",
            "description": "...",
            "severity": "P0",             # P0/P1/P2
            "status": "pending",          # pending | fixed | escalated | timeout
            "found_at": "S3b R0",
            "fixed_at": None,
            "timeout_retry_count": 0,     # 超时重试计数
            "last_timeout_at": None,      # 超时时间戳
            "upgrade_justification": None # 等级升级理由（P1-7）
        },
    ],
    "stats": {
        "total": 0, "fixed": 0,
        "pending": 0, "escalated": 0,
        "timeout_count": 0
    },
    "sg_status": {
        "SG1": "PENDING",                # PENDING | PASSED | FAILED
        "SG2": "PENDING"
    }
}
```

---

## S3c 子步骤详解

### S3c.1 — 收集 fail 项

从 S3b Merge Gate 输出中提取"核心 fail"项（P0/P1），写入 `audit_review_queue.queue`。

**忽略项**：
- Q6 警告项（P2 及以下）
- 已在上一轮 R 迭代中修复的项

### S3c.2 — 派发子代理修复

按 queue 项内容派发子代理修复（Parallel 模式）。

**派发逻辑**：
```python
# 每个 queue 项派发一个子代理
for item in audit_review_queue.queue:
    if item.status == "pending":
        sessions_spawn(
            task=f"修复 audit finding: {item.id} - {item.description}",
            agentId=get_fix_agent(item.severity),
            label=f"s3c-fix-{item.id}",
            mode="run"
        )
```

**SG1 门禁（S3c.2 → S3c.3 过渡）**：

| ID | 条件 | 量化标准 |
|----|------|---------|
| SG1.1 | P0 问题清零 | 所有 P0 已修复，或标记为"已知/接受" |
| SG1.2 | P1 修复率 ≥ 80% | `fixed_p1 / total_p1 >= 0.8` |
| SG1.3 | 子代理成功率 ≥ 60% | `completed_spawns / total_spawns >= 0.6` |
| SG1.4 | 无新增 P0 问题 | 本次 S3c.2 修复中不引入新 P0 |

**特殊处理**：
- `spawn_success_rate == 0.0` → **强制降级主会话**（`mandatory_override = True`）
- `0.0 < spawn_success_rate < 0.6` → 降级建议

**SG1 判定分支**：
```
SG1 判定
  ├── 全部通过 → ✅ 进入 S3c.3
  ├── SG1.3 失败（成功率 < 60%）→ 降级主会话 + 继续 S3c.3
  ├── SG1.1/SG1.4 失败 → ❌ 阻塞，返回 S3c.2 重新派发
  └── SG1.2 失败（修复率 < 80%）→ 主会话接管剩余 P1 → 进入 S3c.3
```

### S3c.3 — 验证修复充分性

检查每个 queue 项的修复报告和修复文件，确保：
1. 修复报告已写入
2. 修复文件确实被修改
3. 修改内容与修复报告一致

**验证方法**：引用 `fact_check.py` 的 `verify_source_claims()`。

### S3c.4 — 回归 S3b Merge Gate

仅重审 queue 项对应的 S4 结果，验证修复是否真正解决了问题。

**SG2 门禁（S3c.4 → S5/S3c.1 过渡）**：

| ID | 条件 | 量化标准 | 说明 |
|----|------|---------|------|
| SG2.1 | P0 问题 = 0 | 复审未发现新 P0 | 不变 |
| SG2.2 | P1 问题 ≤ 3 个 | 新 P1 数量可控 | 不变 |
| SG2.3 | 等级升级有 justification | 升级必须有书面理由 | v3.0"有升级须理由" |
| SG2.4 | 验证记录完整 | 每个修复项有对应测试/验证记录 | 不变 |

**SG2.3 详细规则**：
```
SG2.3 判定逻辑：
  ├── 无等级升级 → ✅ 通过（正常情况）
  ├── 有等级升级 + 有 upgrade_justification → ⚠️ 警告（允许继续）
  └── 有等级升级 + 无 upgrade_justification → ❌ 阻塞
```

`upgrade_justification` 字段格式：
```json
{
  "finding_id": "FINDING-005",
  "original_severity": "P2",
  "upgraded_severity": "P0",
  "reason": "复审发现该问题涉及agent_id冒名顶替可导致会话劫持，原评级偏低",
  "reviewer": "SG2 R1 审计",
  "timestamp": "2026-05-29T22:XX:XX+08:00"
}
```

**SG2 判定分支**：
```
SG2 判定
  ├── 全部通过（含 SG2.3 WARN）→ ✅ 迭代完成，进入 S5 归档
  ├── 未通过（≤3个新 P1，SG2.1/SG2.3/SG2.4 通过）→ 跳转 S3c.1（R+1 迭代）
  ├── 未通过（>3个新 P1 或有新 P0）→ 主会话直审 → S3c R2
  ├── SG2.3 FAIL（无升级理由）→ ❌ 阻塞，补充后重新判定
  └── R2 后仍未通过 → 记录超限警告 + 主会话决策（上报用户）
```

---

## 超时恢复策略

**引用标准协议**：`subagent-timeout-recovery.md`（L3 冷数据，超时关键词触发）

**超时恢复步骤**：
1. 检查 queue 项状态（fix report 是否已写入？）
2. 检查修复文件修改时间是否在超时之后（部分成功检测）
3. 如果是"超时但写入成功"→ 标记 fixed，不再重试
4. 重新 spawn 单个 queue 项任务（避免连锁超时）

**全部子代理超时（0%成功率）处理**：
- `spawn_success_rate == 0.0` → 强制降级主会话（`mandatory_override = True`）
- 触发 B4.1 根因分析（判断是否为 gateway 系统性问题）
- 与 SG1.3（成功率 < 60% → 降级建议）区分

---

## checkpoint 写入时机

| 时机 | 说明 |
|------|------|
| S3c.4 完成后 | 每次迭代完成写入 checkpoint |
| 全部子代理超时 | 写入 checkpoint（含 sg_status.exceeded）|
| sessions_yield 前 | 主会话 yield 前写入 checkpoint |

**checkpoint 路径**：`~/.qclaw/skills/auditor/_checkpoints/`

**checkpoint 清理**：参见 `_knowledge/_components/checkpoint-cleanup.md`

---

## 与 Step-Gate 框架关系

SG1/SG2 是 S3c.2 和 S3c.4 的门禁机制：

| Step-Gate | 嵌入点 | 作用 |
|-----------|--------|------|
| **SG1** | S3c.2 → S3c.3 | 子代理修复完成后，检查是否满足进入 S3c.3 的条件 |
| **SG2** | S3c.4 → S5/S3c.1 | 回归 S3b 完成后，检查是否满足退出 S3c 循环的条件 |

详见 SKILL.md Phase-S 末尾「Step-Gate 框架」附录。

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-30 | 初始版本（基于 v3.1 synthesis）|