# S2/S4 子代理协调协议

> 版本：v1.0 | 状态：active
> 来源：auditor Layer0 S2/S4 子代理管理
> 定位：S2 规划合并 / S4 执行验证的子代理协调

---

## 执行模式

| 模式 | 适用场景 | 并行度 | 结果 |
|------|---------|--------|------|
| **Single** | 简单变更，单次任务 | 1 | 串行执行 |
| **Parallel** | 并行任务，2-5个子任务 | N | 并行执行 |
| **Pipeline** | 串行依赖，2-3个阶段 | 2-3 | 流水线 |

---

## S2 — 规划合并

**触发**：L1串行 或 有并行风险

### Single 模式（S2）

```powershell
# S2 -N执行 sessions_spawn 创建单个规划代理
sessions_spawn -Task "<规划任务>" -AgentId "<agent-id>" -Timeout 120
```

### Parallel 模式（S2）

当 change_steps > 3 个时，识别并行机会：

```powershell
# sessions-helper.ps1 Parallel 模式
sessions-helper.ps1 -ParallelTasks @(
  @{Task="任务1"; AgentId="..."; Timeout=120},
  @{Task="任务2"; AgentId="..."; Timeout=120},
  @{Task="任务3"; AgentId="..."; Timeout=120}
) -MaxConcurrency 3
```

---

## S4 — 执行+验证

**触发**：L3+强制 / L1/L2可选

### 8项验证（必须全部通过）

| # | 验证项 | 说明 |
|---|--------|------|
| 1 | 文件存在性 | 目标文件是否存在 |
| 2 | 数值一致性-A | 配置值与预期一致 |
| 3 | 数值一致性-B | 跨文件引用值一致 |
| 4 | 资源标识 | ID/名称唯一性 |
| 5 | 路径正确性 | 引用路径有效 |
| 6 | 逻辑正确性 | 业务逻辑无矛盾 |
| 7 | 前序结果 | 前序步骤输出被正确使用 |
| 8 | 版本一致性 | 版本号/标签一致 |

### Parallel 执行（S4）

```powershell
sessions-helper.ps1 -ParallelTasks @(
  @{Task="验证文件存在"; AgentId="..."; Timeout=60},
  @{Task="验证数值一致性"; AgentId="..."; Timeout=60},
  @{Task="验证资源标识"; AgentId="..."; Timeout=60},
  @{Task="验证路径正确性"; AgentId="..."; Timeout=60},
  @{Task="验证逻辑正确性"; AgentId="..."; Timeout=60},
  @{Task="验证前序结果"; AgentId="..."; Timeout=60},
  @{Task="验证版本一致性"; AgentId="..."; Timeout=60}
) -MaxConcurrency 4
```

### S4.1 内容层检查记录

| 检查项 | 状态 | 发现 |
|--------|------|------|
| 阈值一致性 | pass/fail/不适用 | {列出阈值不一致项} |
| 数据新鲜度 | pass/fail | {列出超过24小时的陈旧数据项} |
| 跨文件引用 | pass/fail | {列出引用路径错误项} |

---

## 协调参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `max_retries` | 3 | 最大重试次数 |
| `timeout_seconds` | 90 | 单个子代理超时 |
| `max_concurrency` | 4 | 最大并行数 |
| `on_fail` | throw | 失败时动作 |

---

## S3c — 子代理协调（Review Loop）

**触发**：S3b Merge Gate 发现 P0/P1 fail 项

### S3c.2 — 派发子代理修复

```powershell
# 每个 queue 项派发一个子代理（Parallel 模式）
sessions-helper.ps1 -ParallelTasks @(
    @{Task="修复 FINDING-001: P0 安全漏洞"; AgentId="PyCoder"; Timeout=180},
    @{Task="修复 FINDING-002: P1 异常处理缺失"; AgentId="PyCoder"; Timeout=180}
) -MaxConcurrency 3
```

**SG1 门禁**（S3c.2 → S3c.3）：成功率 ≥ 60% + P0 清零 + P1 修复率 ≥ 80%


### S3c.3 — 验证修复充分性

调用 `fact_check.py` 逐条验证修复报告与修复文件一致性。

### S3c.4 — 回归 S3b Merge Gate

**SG2 门禁**（S3c.4 → S5/S3c.1）：无新 P0 + 新 P1 ≤ 3 + 升级有 justification

### checkpoint 写入

| 时机 | 写入内容 |
|------|---------|
| S3c.4 完成后 | iteration + queue + sg_status |
| 全部超时 | sg_status.exceeded |
| sessions_yield 前 | 全量 checkpoint |

**路径**：`~/.qclaw/skills/auditor/_checkpoints/`
**清理**：参见 `checkpoint-cleanup.md`

---

## Fallback

若无 sessions-helper.ps1：
- S2/S3c → 串行创建单个子代理
- S4/S3c → 串行执行验证
- 重试超过 max_retries → 标记失败