# 子代理调用模式（F11 / E6）

> 版本：v1.1 | 状态：active | 更新：2026-05-25
> 来源：agent-planner F11 子代理标准化 + E6 多源并行
> 定位：S2/S4/多源读取时的执行层模式选择

---

## ⚠️ Windows+WSL 环境警告（2026-05-22 实测）

> `agent-team spawn subprocess` 在 Windows+WSL 环境下 **0/6 成功率**。
> **所有 spawn 操作必须使用 `sessions_spawn`**，不再使用 agent-team spawn。
> 参考：tools-config.md § agent-team spawn subprocess 彻底不可用

---

## 4级执行路径（F11）

| 级别 | 工具 | 触发条件 | Windows+WSL |
|------|------|---------|------------|
| **L0** | `sessions_spawn`（并行） | 所有 spawn 场景 | ✅ 100% 稳定 |
| **L1** | agent-team TeamCreate（仅WSL内非spawn命令） | 独立验证>3项 + WSL环境 + 非spawn操作 | ⚠️ 仅限 list/status/sync |
| **L2** | asyncio parallel Task | 独立验证>3项 + agent-team spawn 不可用 | ❌ subprocess 0% |
| **L3** | sessions_spawn 串行 | 终极兜底 | ✅ 唯一选择 |

> **L0 是默认选择**。L1 仅限 WSL 内非 spawn 运维命令。L2/L3 仅在特殊场景使用。

---

## sessions_spawn 参数规范（F11）

| 参数 | 必填 | 说明 |
|------|------|------|
| label | ✅ | 子代理名称，格式 `{role}-{seq}` |
| mode | ✅ | `run`（一次性任务）/ `session`（持久会话） |
| runtime | ❌ | 默认 `subagent` |
| task | ✅ | 任务描述，200字内 |
| runTimeoutSeconds | ❌ | 超时秒数，默认无限制 |

---

## agent-team vs sessions_spawn 选择

| 场景 | 工具选择 | 原因 |
|------|---------|------|
| 派生子代理执行任务 | `sessions_spawn` | 直接访问主会话context，100%稳定 |
| WSL内运维命令（list/status/sync） | agent-team | tmux会话支持，WSL内运行 |
| 复杂多步骤任务 | `sessions_spawn` | 支持多轮对话 |
| 轻量并行验证 | `sessions_spawn × N` | 并行分发，无额外进程 |

> ⚠️ **禁止在 Windows+WSL 环境下使用 `agent-team spawn subprocess`**，无论任何理由。

---

## E6 多源并行读取

**触发条件**：≥3个独立来源读取信息时

**执行规则**：
1. 优先使用 `sessions_spawn` fan-out 并行模式
2. Task 为主：多个 Task 并行读取
3. ClawTeam 为可选：WSL/tmux 环境下降级为 sessions_spawn
4. 每个来源结果必须独立记录
5. 超时处理：单源超时30s后跳过，标注"来源X超时"

**降级规则**：
1. ClawTeam worker EXIT → 降级 sessions_spawn
2. ClawTeam spawn 超时>30s → 降级 sessions_spawn
3. ClawTeam 未安装 → 降级 sessions_spawn

**输出格式**：
```json
{
  "sources_total": 5,
  "findings": [
    {"source": "path/to/file", "status": "ok|error", "key_data": "摘要", "anomaly": null|"异常描述"}
  ],
  "report_summary": "N个文件已读取，X个异常"
}
```

---

## 并行执行增强参考

> 更多并行执行细节（含DAG调度/T6-T10避坑/Tier-3场景方案）：
> 引用 `multi-thread-execution` → `references/scheme.md`