---
name: skill-audit-suite
description: "CI/CD skill audit integration for auditor Layer A. Scans installed skills for security issues, missing dependencies, and hook readiness. Triggers on: skill scan, audit skill, check skill health."
version: 1.0.0
---

# skill-audit-suite v1.0

CI/CD skill audit integration — auditor Layer A 的具体实现。

## 功能

| 功能 | 说明 |
|------|------|
| 扫描已安装 skills | 检查 SKILL.md 缺失、资源文件缺失、触发词冲突 |
| 依赖检查 | skill 依赖的 CLI/工具是否可用 |
| Hook 就绪检查 | 检查是否有 `_hooks/` 目录和有效 hook 脚本 |
| 安全扫描 | 检测危险 API 调用（`rm -rf` / 硬编码凭证等） |

## 扫描命令

```bash
# 扫描所有 skills
python scripts/scan-skills.py --all

# 扫描单个 skill
python scripts/scan-skills.py --skill auditor

# 输出 JSON 格式（供 auditor 消费）
python scripts/scan-skills.py --all --json

# 检查某 skill 的钩子
python scripts/check-hooks.py --skill agent-team
```

## 与 auditor Layer A 集成

auditor S1 准备项检查时，调用：

```bash
python $SKILL_DIR/skill-audit-suite/scripts/scan-skills.py --all --json
```

结果注入 `audit_skills_ready` 字段：
- `true` = 所有 M 类 skill 依赖可用
- `false` = 部分缺失，auditor 降级 Layer A 并警告