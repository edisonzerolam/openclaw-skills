# residual-generator — 残余变更 Cron 生成器

> 版本：v1.0
> 用途：为"改不完"的规划变更自动生成定时提醒 cron
> 调用时机：每次规划迭代后，发现有待实施变更时调用

---

## 核心逻辑

```
输入：{plan-id}.json（Tracker 文件）
输入：要生成 cron 的变更列表 [chg-001, chg-002, ...]

输出：一组 cron job 对象（供 cron add 工具使用）

决策逻辑：
1. 遍历变更列表
2. 对每个 status="pending" 的变更：
   a. 检查 dueAt：
      - 有 dueAt 且在7天内 → 生成"一次性提醒"（kind: at）
      - 有 dueAt 但在7天后 → 生成"每日提醒"（kind: cron）
      - 无 dueAt → 使用默认：规划完成 +24h 生成一次性提醒
   b. 生成 cron payload（见下）
3. 如所有变更均已 applied → 不生成任何 cron
```

---

## Cron Payload 模板

### 模式A：一次性提醒（kind: at）

适用于：dueAt 在7天内的变更
```json
{
  "name": "【规划追踪】{planName} 变更 #{chg-id} 提醒",
  "schedule": {
    "kind": "at",
    "at": "{dueAt ISO8601}"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "【规划执行提醒：{planName} #{chg-id}】\n\n请检查规划变更是否已实施。\n\n读取 ~/.qclaw/workspace-mentor_agent/shared/plan-tracker/{plan-id}.json\n\n在 changes[] 中找到 id=\"{chg-id}\"：\n- 如果 status=\"applied\"：\n  → 不发送任何消息，静默结束\n- 如果 status=\"pending\"：\n  → 使用 message 工具发送到 channel=wechat-access：\n  \"⚠️ 规划变更待实施提醒\\n━━━━━━━━━━━━━━━━━━\\n规划：{planName}\\n变更：{chg-description}\\n目标：{chg-target}\\n状态：pending\\n━━━━━━━━━━━━━━━━━━\\n请尽快实施或确认跳过。\"",
    "timeoutSeconds": 60
  },
  "delivery": {
    "mode": "announce",
    "channel": "openclaw-weixin",
    "to": "o9cq80ysJb5OJRTFii0tkPhVbY_0@im.wechat",
    "bestEffort": true
  },
  "enabled": true
}
```

### 模式B：每日提醒（kind: cron）

适用于：dueAt 在7天后或未指定（默认24h后）
```json
{
  "name": "【规划追踪】{planName} 变更 #{chg-id} 提醒",
  "schedule": {
    "kind": "cron",
    "expr": "{每日触发时间}",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "【规划执行提醒：{planName} #{chg-id}】\n\n请检查规划变更是否已实施。\n\n读取 ~/.qclaw/workspace-mentor_agent/shared/plan-tracker/{plan-id}.json\n\n在 changes[] 中找到 id=\"{chg-id}\"：\n- 如果 status=\"applied\"：\n  → 不发送任何消息，静默结束\n- 如果 status=\"pending\"：\n  → 使用 message 工具发送到 channel=wechat-access：\n  \"⚠️ 规划变更待实施提醒\\n━━━━━━━━━━━━━━━━━━\\n规划：{planName}\\n变更：{chg-description}\\n目标：{chg-target}\\n状态：pending\\n━━━━━━━━━━━━━━━━━━\\n请尽快实施或确认跳过。\"",
    "timeoutSeconds": 60
  },
  "delivery": {
    "mode": "announce",
    "channel": "openclaw-weixin",
    "to": "o9cq80ysJb5OJRTFii0tkPhVbY_0@im.wechat",
    "bestEffort": true
  },
  "enabled": true,
  "deleteAfterRun": false
}
```

---

## Agent 执行步骤

### RG1: 生成残余 Cron

```
输入：{plan-id}.json
输入：变更列表 [chg-001, chg-002, ...]

步骤：
1. 读取 {plan-id}.json
2. 遍历变更列表，过滤 status="pending"
3. 对每个 pending 变更：
   a. 确定 dueAt（读取变更的 dueAt 字段）
   b. 确定触发模式（一次性 vs 每日）
   c. 生成 cron payload
4. 汇总所有 cron 对象
5. 逐一调用 cron add 工具
6. 将生成的 reminderCronId 填入对应变更的 reminderCronId 字段
7. 覆盖写入 {plan-id}.json
8. 输出：已创建 N 个残余提醒 cron
```

### RG2: 清理失效 Cron

```
输入：{plan-id}.json

步骤：
1. 读取 {plan-id}.json
2. 遍历所有 changes[] 中 reminderCronId 非 null 的变更
3. 如果变更 status="applied" 或 status="skipped"：
   a. 调用 cron remove 删除 reminderCronId 对应的 cron
   b. 将变更的 reminderCronId 设为 null
4. 覆盖写入 {plan-id}.json
```

---

## 决策矩阵

| dueAt | 距今天数 | Cron 类型 | schedule |
|-------|---------|----------|---------|
| 已指定 | ≤7天 | kind: at（一次性） | dueAt 精确时间 |
| 已指定 | >7天 | kind: cron（每日） | 每天固定时间 |
| 未指定 | — | kind: at（一次性） | 规划完成时间 +24h |
| 已过期 | — | kind: at（一次性） | 立即（当前时间 +5min） |

---

## 与 Tracker 的集成

```
residual-generator 是 tracker 的执行器：
- Tracker 负责存储变更状态
- Residual-generator 负责生成/删除 cron

典型流程：
1. 规划迭代完成（T2）
2. 发现 chg-002 状态为 pending，dueAt=2026-04-28
3. 调用 RG1 → 生成 kind:at cron，dueAt=2026-04-28T09:00:00+08:00
4. 2026-04-28 cron 触发 → 检查 status=pending → 推送 wechat-access
5. 老板实施变更 → Agent 调用 T3 标记 applied
6. Agent 调用 RG2 → 清理对应 cron，reminderCronId=null
```

---

## 输出格式

```json
{
  "generatedCrons": [
    {
      "chgId": "chg-002",
      "cronId": "生成的 cron job id",
      "schedule": "2026-04-28T09:00:00+08:00",
      "type": "at"
    }
  ],
  "cleanedCrons": [],
  "unchangedCrons": []
}
```
