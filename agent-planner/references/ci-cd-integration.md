# CI/CD Integration — agent-planner v3.2

> 版本：v1.0 | 状态：active
> 来源：chg-004 audit finding
> 定位：提供 CI/CD 流水线集成参考

## 目录结构检查（Audit Hook）

每次变更后自动检查以下文件完整性：

```
_inline/
  plan-template.md           → 必须存在
  spawn-patterns.md           → 必须存在
  workspace-zones.md         → 必须存在
  pitfall-library.md          → 必须存在
  knowledge-base-integration.md → 必须存在
  plan-tracker/
    tracker.md                → 必须存在
    residual-generator.md     → 必须存在
    evolution-log.md           → 必须存在
```

## Hash 校验

```bash
# frozen_version.json hash 必须与实际文件一致
$ jq '.files[]' frozen_version.json
```

## 行为红线检查集成

R1~R5 规则通过 `behavior-checker.ps1` 集成：

```powershell
.\behavior-checker.ps1 -AuditTarget "C:\path\to\agent-planner" -FullAudit
```

## 变更门禁

| 阶段 | 检查项 | 阻塞条件 |
|------|--------|---------|
| pre-commit | 文件完整性扫描 | `plan-tracker/` 目录缺任意文件 |
| pre-commit | frozen_version.json 同步 | hash 不匹配 |
| pre-commit | 行为红线扫描 | R1/R3/R4 触发 block |
| pre-commit | 嵌套目录扫描 | 深度>1 的嵌套目录 |

## 禁止事项

- 禁止创建 `agent-planner/agent-planner/` 类嵌套副本
- 禁止 `frozen_version.json` 为空
- 禁止跨 agent 硬编码路径（如 `~/.qclaw/workspace-mentor_agent/`）
