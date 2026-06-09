# plan-tracker — 规划版本追踪核心逻辑

> 版本：v1.0
> 维护：agent-planner v3.4 内置子模块
> 路径：~/.qclaw/skills/agent-planner/_knowledge/_enhancement/plan-tracker/

---

## 核心数据结构

每个规划对应一个 `{plan-id}.json` 文件：

```json
{
  "trackerVersion": "1.0",
  "planId": "{plan-id}",
  "planName": "{规划名称}",
  "createdAt": "ISO8601",
  "currentVersion": "v1",
  "status": "in_progress | completed | abandoned",
  "owner": "agent-planner",
  "description": "{一句话描述}",
  "versions": [
    {
      "version": "v1",
      "createdAt": "ISO8601",
      "createdBy": "agent-planner",
      "summary": "{本次变更摘要}",
      "iteration": 1,
      "changes": [
        {
          "id": "chg-001",
          "description": "{变更描述}",
          "type": "cron_payload | new_file | skill_config | agent_config | manual_step | other",
          "target": "{目标标识，如 job:xxx 或 path:xxx}",
          "priority": "P0 | P1 | P2",
          "appliedAt": null,
          "status": "pending | applied | skipped | blocked",
          "appliedBy": null,
          "reminderCronId": null,
          "dueAt": null,
          "notes": "{备注}"
        }
      ]
    }
  ],
  "pendingChanges": [],
  "completedChanges": [],
  "nextReminder": null
}
```

### type 字段说明

| type | 说明 | 目标格式 |
|------|------|---------|
| cron_payload | 修改 cron 任务内容 | `job:{jobId}` |
| new_file | 新建文件/目录 | `path:{绝对路径}` |
| skill_config | 修改 skill 配置 | `skill:{skillName}` |
| agent_config | 修改 agent 配置 | `agent:{agentId}` |
| manual_step | 需手动操作 | `step:{描述}` |
| other | 其他 | `ref:{描述}` |

### status 流转

```
pending → applied（实施后）
pending → skipped（确认跳过）
pending → blocked（因依赖无法实施）
```

---

## Tracker 操作 API（Agent 执行步骤）

### T1: 创建 Tracker

```
触发时机：用户说"规划后审查" / "分多次修改" / "改不完" / 其他时间修改

前置：
1. 读取 {workspace_root_dir}/plan-tracker/ 目录
2. 检查是否存在同名 planId.json（存在则追加版本，而非覆盖）
3. 生成 planId（中文规划名 → 拼音/英文单词，如"定时任务联动" → "timed-task-linkage"）

步骤：
1. 生成 tracker JSON（含 trackerVersion: "1.0"）
2. 写入 {workspace_root_dir}/plan-tracker/{plan-id}.json
3. 在 SKILL.md 的演进日志（附录）中追加一行
```

### T2: 追加版本记录

```
触发时机：每次规划迭代（v1→v2→v3）

步骤：
1. 读取现有 {plan-id}.json
2. 生成新版本块（version = v{N+1}, iteration++, currentVersion 更新）
3. 将新版本 changes[] 写入（变更清单由规划输出提供）
4. 覆盖写入 {plan-id}.json
```

### T3: 标记变更已实施

```
触发时机：F2 确认后，Agent 实际执行了变更

步骤：
1. 读取 {plan-id}.json
2. 在对应版本的 changes[] 中找到对应 chg-id
3. appliedAt = 当前时间
4. status = "applied"
5. appliedBy = "agent-planner"
6. 从 pendingChanges[] 移除，追加到 completedChanges[]
7. 覆盖写入
```

### T4: 查询待实施变更

```
步骤：
1. 读取 {plan-id}.json
2. 过滤 status="pending" 的 changes[]
3. 按 dueAt 排序
4. 输出待实施清单
```

### T5: 生成残余提醒 Cron

详见 `residual-generator.md`

---

## planId 命名规范

```
格式：{英文名}-{日期}
示例：
- timed-task-linkage-2026-04-26
- fund-workflow-v3-2026-04-26

生成规则：
- 中文 → 拼音首字母 → 英文意译
- 保留原日期（首次创建日期）
- 避免特殊字符（仅 - 和 _）
```

---

## 文件存储路径

```
{workspace_root_dir}/plan-tracker/
├── timed-task-linkage-2026-04-26.json   — 定时任务联动方案追踪文件
├── fund-workflow-v3-2026-04-25.json     — 基金流程v3追踪文件
└── evolution-log.md                      — 跨规划演进总日志
```

---

## 与 cron 工具集成

```
关键集成点：
1. 创建 Tracker 时，不自动创建 cron
2. 每次规划迭代后，由 Agent 显式调用 residual-generator 生成 cron
3. Cron 执行时读取 {plan-id}.json，检查对应 chg 是否已 applied
4. 已 applied → 静默结束；未 applied → 推送 wechat-access 提醒
```

---

## 与现有 SKILL.md 流程集成

在现有规划流程中，agent-planner 在以下节点操作 Tracker：

| 节点 | 操作 |
|------|------|
| 规划启动（F1之前） | T1 创建 Tracker（如触发条件满足） |
| 规划迭代完成（F2之前） | T2 追加版本记录 |
| F2 确认通过 | T3 标记已实施 + T4 查询待实施 |
| 发现残余变更 | T5 生成残余 Cron |
| 全部实施完毕 | status = "completed"，停止新 cron 生成 |
