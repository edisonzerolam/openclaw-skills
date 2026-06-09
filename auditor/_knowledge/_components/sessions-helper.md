# S2/S4 子代理协调指南

> 版本：v2.0 | 状态：active  
> 替代：原 sessions-helper.ps1（已废弃，因 `openclaw` CLI 不存在）

## 执行模式

| 模式 | 适用场景 | 调用方式 |
|------|---------|---------|
| Single | 简单变更，单次任务 | `sessions_spawn` 单次调用 |
| Parallel | 并行任务，2-5 个子任务 | `sessions_spawn` × N + `subagents` 监控 |
| Pipeline | 串行依赖，2-3 个阶段 | 串行 `sessions_spawn`，结果传递 |

## Single 模式（S2）

使用 OpenClaw 内置 `sessions_spawn` 工具：

```json
{
  "runtime": "subagent",
  "mode": "run",
  "task": "<规划任务描述>",
  "timeoutSeconds": 120
}
```

**示例**：创建单个规划子代理
- runtime: "subagent"
- mode: "run"
- task: "分析当前 skill 的架构问题，输出优化建议"
- timeoutSeconds: 120

## Parallel 模式（S4 验证）

并发执行 8 项验证，每项一个 subagent：

| # | 验证项 | 任务描述 |
|---|--------|---------|
| 1 | 文件存在性 | 检查目标文件是否存在 |
| 2 | 数值一致性-A | 配置值与预期一致 |
| 3 | 数值一致性-B | 跨文件引用值一致 |
| 4 | 资源标识 | ID/名称唯一性 |
| 5 | 路径正确性 | 引用路径有效 |
| 6 | 逻辑正确性 | 业务逻辑无矛盾 |
| 7 | 前序结果 | 前序步骤输出被正确使用 |
| 8 | 版本一致性 | 版本号/标签一致 |

**执行方式**：
1. 为每项验证创建独立的 `sessions_spawn` 调用
2. 使用 `subagents` 工具监控执行状态
3. 汇总所有结果

**注意**：由于 OpenClaw 的 `sessions_spawn` 是异步的，Parallel 模式需要手动管理并发。

## Pipeline 模式（多阶段）

```
阶段 1: sessions_spawn → 获取规划结果
    ↓
阶段 2: sessions_spawn（task 包含阶段 1 结果）→ 执行变更
    ↓
阶段 3: sessions_spawn（task 包含阶段 2 结果）→ 验证
```

## 协调参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| timeoutSeconds | 120 | 单个子代理超时 |
| maxConcurrency | 4 | 最大并行数（手动控制） |
| maxRetries | 3 | 最大重试次数 |

## Fallback

若 `sessions_spawn` 不可用：
- S2 → 在当前会话中串行执行规划
- S4 → 在当前会话中串行执行 8 项验证
- 重试超过 maxRetries → 标记失败

## 与 agent-team 的对比

| 特性 | agent-team | OpenClaw sessions_spawn |
|------|----------|------------------------|
| 平台 | Linux/WSL | 跨平台 |
| 团队管理 | 完整（team/inbox/task） | 无（仅 spawn） |
| 状态持久化 | 有（snapshot/restore） | 无 |
| 适用场景 | 复杂多 agent 团队 | 简单子任务委托 |
| Windows | 需 WSL | 原生支持 |

**建议**：
- 简单审计（1-2 个子代理）→ 使用 `sessions_spawn`
- 复杂团队（3+ agent 协作）→ 使用 agent-team（WSL 环境）
