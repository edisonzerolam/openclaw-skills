---
name: debug
description: "Trace errors in log files, parse stack traces, detect memory leaks, profile commands, and debug HTTP. 触发词：debug, diag, trace, stacktrace, crash, log. 不适用：非错误诊断类查询、代码审查。"
version: "3.4.0"
---

## 需求路由

| 需求类型 | 路由 | 说明 |
|---------|:----:|------|
| trace /var/log/syslog | local | debug-core.js trace |
| 分析堆栈根本原因 | llm | LLM 根因诊断 |
| 对比两个日志文件 | local | debug-core.js diff-logs |
| 内存泄漏根因 | llm | LLM 诊断 |

## 命令概览

| 命令 | 路径 | 用途 |
|------|------|------|
| `trace` | `scripts/script.sh trace <file>` | 日志错误模式分析 |
| `stacktrace` | `scripts/script.sh stacktrace <file>` | 堆栈解析 |
| `leaks` | `scripts/script.sh leaks --pid <id>` | 内存泄漏检测 |
| `profile` | `scripts/script.sh profile <cmd>` | 性能剖析 |
| `diff-logs` | `scripts/script.sh diff-logs <a> <b>` | 日志差异对比 |
| `http` | `scripts/script.sh http <url>` | HTTP 调试（含 SSL/重定向/耗时）|
| `selfcheck` | `scripts/script.sh selfcheck` | 脚本自检（语法/依赖/退出码）|
| `format` | `scripts/script.sh format --output json\|csv\|md` | 结构化输出 |

> **退出码**：0=OK / 1=ERR_FOUND / 2=WARN / 3=PERM / 4=TIMEOUT / 5=CONFIG / 64=USAGE

详见 `_knowledge/references/commands-detail.md`。

## 模块化架构

```
scripts/
  script.sh          # 主路由器（~50行）
  config.toml        # 默认配置
  lib/               # exit_codes.sh, config.sh, common.sh
  cmd/               # 各命令独立 .sh 文件
```

`config.toml` 可调整默认值（pattern/max_depth/timeout 等），无需改代码。
详见 `_knowledge/references/commands-detail.md#configtoml`。

## 增强层索引

| 层级 | 文件 | 加载时机 |
|:----:|------|:--------:|
| **L1** | SKILL.md（核心命令） | 首次加载 |
| **L2** | `_knowledge/knowledge-health-check.md` | SKILL.md 后 |
| **L2** | `_knowledge/knowledge-error-patterns.md` | 诊断/错误/修复触发 |
| **L3** | `_knowledge/scripts/` | 批量验证/调试触发 |
| **L3** | `_knowledge/knowledge-windows-debug.md` | windows/powershell/bsod |
| **L4** | `_knowledge/references/` | 专家模式（--expert / 复杂/长尾）|

**并行支持**（`[[PARALLEL]]`）：leaks 多进程、profile 多命令、http 多端点、trace 多模式

## 参考文件

| 文件 | 用途 |
|------|------|
| `_knowledge/references/commands-detail.md` | 命令详细语法 + config.toml |
| `_knowledge/references/self-learning.md` | 自学习 + 事实核查 + 跨 skill 反馈 |
| `_knowledge/knowledge-error-patterns.md` | 12 类错误模式库 |
| `_knowledge/knowledge-health-check.md` | 健康检查标准 |
| `_knowledge/knowledge-windows-debug.md` | Windows 调试 |
| `_knowledge/references/` | 专家知识池（按领域）|

## 故障与降级

| 场景 | 处理 |
|------|------|
| script.sh 自检失败 | 跳过本地执行，回退到 LLM 诊断 |
| fact_check.py 不可达 | 回退到 exec 验证 |
| 专家知识库不可读 | 跳过 L4 加载，使用 L1-L3 能力 |