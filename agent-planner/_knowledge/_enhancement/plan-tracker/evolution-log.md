# evolution-log — 规划演进记录格式

> 版本：v1.0
> 用途：跨规划版本的演进记录，供夜间精炼任务和 Agent 自我学习使用
> 路径：~/.qclaw/workspace-mentor_agent/shared/plan-tracker/evolution-log.md

---

## 记录格式

每行一条记录，严格按以下格式追加：

```
| {日期} | {planId} | v{N} | {变更数} | {已实施} | {待实施} | {状态} | {规划摘要} |
```

### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| 日期 | 最后更新日期 | 2026-04-26 |
| planId | 规划唯一标识 | timed-task-linkage-2026-04-26 |
| v{N} | 当前版本号 | v3 |
| 变更数 | 累计变更条目数 | 11 |
| 已实施 | 状态为 applied 的变更数 | 8 |
| 待实施 | 状态为 pending 的变更数 | 3 |
| 状态 | in_progress / completed / abandoned | in_progress |
| 规划摘要 | 一句话描述本次变更核心 | 审计后修正：增加降级机制 |

---

## 完整演进日志示例

```markdown
# evolution-log — 跨规划演进记录

| 日期 | planId | 版本 | 变更数 | 已实施 | 待实施 | 状态 | 规划摘要 |
|------|--------|------|--------|--------|--------|------|---------|
| 2026-04-26 | timed-task-linkage-2026-04-26 | v1 | 5 | 0 | 5 | in_progress | 初始规划：三链三档架构设计 |
| 2026-04-26 | timed-task-linkage-2026-04-26 | v2 | 3 | 0 | 8 | in_progress | 审计后修正：增加降级兜底机制 |
| 2026-04-26 | timed-task-linkage-2026-04-26 | v3 | 3 | 3 | 3 | in_progress | 最终方案：实施批次+残余cron |
| 2026-04-26 | agent-planner-upgrade-2026-04-26 | v1 | 5 | 0 | 5 | in_progress | agent-planner v3.1升级规划 |
```

---

## Agent 操作规范

### EL1: 新增规划记录

```
触发时机：T1 创建 Tracker 时同步追加一行

步骤：
1. 读取 evolution-log.md（如不存在则创建）
2. 追加一行（空值填充未决字段）
3. 写入
```

### EL2: 更新演进记录

```
触发时机：每次规划迭代后（T2 追加版本后同步更新）

步骤：
1. 读取 evolution-log.md
2. 找到对应 planId 的行
3. 更新：版本、变更数、已实施、待实施、状态、规划摘要
4. 写回
```

### EL3: 标记规划完成

```
触发时机：所有变更均已 applied（status=completed）

步骤：
1. 读取 evolution-log.md
2. 找到对应 planId 的行
3. 更新状态为 "completed"，待实施改为 0
4. 写回
5. 可选：将该规划从 active 列表移至归档区（在日志内标记 [ARCHIVED]）
```

---

## 跨规划学习使用

evolution-log.md 是 Agent 自我学习的关键数据源：

| 学习场景 | 使用方式 |
|---------|---------|
| 夜间精炼 | 统计 in_progress 规划数、平均实施周期 |
| 自我进化 | 发现"规划多次被搁置"的模式 → 升级到 capability-evolver |
| 经验沉淀 | 待实施 >5 的规划 → 触发预警，提醒用户收敛 |

---

## 与其他模块的关系

```
evolution-log.md
    ↑
    │ 被更新
    │
tracker.md ← 每次版本追加时同步更新 evolution-log
    ↑
    │ 提供数据
    │
residual-generator.md ← 读取 pending 数用于 cron 生成决策
```
