# agent-planner 工作流（F4-F12）

## F4 — 架构方案

产出内容：Agent 组成 / rules.md 结构 / identity-config.md / 通信机制 / 降级策略

详见 `_knowledge/_enhancement/plan-template.md`。

## F5 — 技能选型（KANO 模型）

| KANO | 优先级 | 说明 |
|------|:------:|------|
| M 必备型 | 必装 | 无则失败 |
| O 期望型 | 推荐 | 做完满意 |
| A 魅力型 | 可选 | 锦上添花 |

MVP 只含 M 类。

## F6 — 工作流编排（4-A + 4-B）

- Epic → Task → Step 三级分解
- 每个 Task 标注：产出物 / 依赖 / 优先级 / 风险 / 并行属性 / 执行嵌入
- 降级状态：L1? / L2?? / L3? / L4??

**并行支持**（`[[PARALLEL]]`）：
- Epic 内多 Task 并行（无依赖）
- 多 Zone Workspace 同时检查
- 批量 spawn 子代理并行执行

**调度规则**：主会话 `sessions_spawn` 并行分发 → 子会话独立超时 → 汇总

## F7 — 坑点预警

读取 pitfall-library.md，筛选≥3 个与方案相关的坑点。

**外部经验引用**（v3.4，单向只读）：

```python
EXTERNAL_LEARNING_SOURCES = [
    r"~/.qclaw/skills/auditor/_knowledge/_refined/LEARNINGS.md",
    r"~/.qclaw/skills/debug/_knowledge/_refined/LEARNINGS.md",
]
```

流程：
1. 逐个读取外部 LEARNINGS.md
2. 提取经验条目与当前方案做关键词匹配
3. 匹配到的经验标注来源（如 `[来源: auditor LEARNINGS]`）
4. 注入坑点预警表格

> **注意**：仅读取，不写入外部 skill 文件。

## F8 — 环境配置清单

| 依赖 | 版本要求 | 验证命令 | 安装方式 |
|------|---------|---------|---------|

## F9 — Workspace 卫生检查

基于 4-Zone 模型。详见 `_knowledge/_enhancement/workspace-zones.md`。

## F10 — 适用场景与边界

明确方案的适用和不适用场景。

## F11 — 子代理调用模式

详见 `_knowledge/_enhancement/spawn-patterns.md`。

3 级执行路径：
- **L1**: agent-team TeamCreate（已废弃，Windows+WSL 0/6 成功率）
- **L2**: Task parallel（`sessions_spawn × N` 并行分发）
- **L3**: sessions_spawn 串行（兜底）

## F12 — 交付后追踪

详见 `_knowledge/_enhancement/plan-tracker/tracker.md`。

| 操作 | 说明 |
|------|------|
| T1 | 创建 Tracker |
| T2 | 追加版本记录 |
| T3 | 标记变更已实施 |
| T4 | 查询待实施变更 |
| T5 | 生成残余提醒 Cron → `_knowledge/_enhancement/plan-tracker/residual-generator.md` |