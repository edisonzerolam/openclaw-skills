# 增强层注册表 (A-N)

> 版本：v1.1 | 更新：2026-05-30 | 统一管理 auditor 增强层元数据

---

## 注册表

| 层 | Skill | 注入点 | 用途 | 状态 | 路径 |
|----|-------|--------|------|------|------|
| A | skill-audit-suite | S1 | CI/CD/历史审计 | ⚠️ 部分可用 | `_components/skill-audit-suite/` |
| B | behavior-checker | Q6 | 行为红线 R1-R5 | ✅ 可用 | `_components/behavior-checker.md` |
| C | skill-context-hygiene | Q0 | Context 健康检测 | ✅ 可用 | `_components/context-hygiene.md` |
| D | skill-session-manager | S2/S4 | 子会话协调 | ⚠️ 降级 | `_components/session-manager.md` |
| E | agent-planner | P-Sub-P | 规划修正 | ✅ 外部 | `~/.qclaw/skills/agent-planner/` |
| F | deep-research | S1 | 深度调研 | ❌ 未安装 | — |
| G | self-improving | S5.9 | 双引擎进化 | ⚠️ 代码缺陷 | `scripts/self-improve.py` |
| H | agent-team | S2/S4 | 团队执行层 | ⚠️ Windows 不可用 | WSL 包装调用 |
| I | docx/pptx | S5 | 报告生成 | ❌ 未安装 | — |
| J | knowledge-base | S1/S5 | 领域知识 | ❌ 未安装 | — |
| K | s1-quality-attributes | S1 | 5 维质量属性 | ✅ 可用 | `_components/s1-quality-attributes.md` |
| L | financial-compliance | S1/S3/S5 | 财务合规审计 | ✅ 可用 | `_components/financial-compliance.md` |
| M | 多源报告核查 | S1/S3 | 专家小组,多报告,second opinion | ✅ 可用 | `_enhancement/expert-panel-protocol.md` |
| N | Expert Panel Protocol | S2/S3 | 专家小组,4角色,安全专家,可靠性专家 | ✅ 可用 | `_enhancement/expert-panel-protocol.md` |

---

## 依赖关系

```
K (QA) → 依赖 multi-thread-execution skill（QA2-QA5 详细检查）
G (进化) → 依赖 capability-evolver Hub（可选，离线时本地降级）
D (子会话) → 依赖 sessions_spawn 工具（OpenClaw 内置）
H (agent-team) → Windows 需 WSL 包装（见 workspace/tools/agent-team-wsl.ps1）
```

---

## 降级策略

| 层 | 降级条件 | Fallback 行为 |
|----|---------|--------------|
| A | scripts 目录缺失 | 跳过 CI/CD 历史检查 |
| D | sessions_spawn 不可用 | 当前会话串行执行规划/验证 |
| F | 未安装 | 跳过深度调研，使用 S1 基础评估 |
| G | capability-evolver 离线 (127.0.0.1:19820) | 仅本地记录到 frozen_version.json |
| H | Windows 无 WSL | 使用 OpenClaw 原生 sessions_spawn 替代 |
| I | 未安装 | 输出纯文本/Markdown 报告 |
| J | 未安装 | 跳过知识库加载 |

---

## 加载策略

### 热数据区（首次加载）
| 文件 | 大小 | 加载时机 |
|------|------|---------|
| knowledge-enhancement-audit.md | ~14 KB | SKILL.md 加载后立即 |

### 冷数据区（按需加载）
| 文件 | 大小 | 触发关键词 |
|------|------|-----------|
| subagent-timeout-recovery.md | ~16 KB | 超时/恢复/重试 |
| multilang-content-handling.md | ~15 KB | 中文/LaTeX/公式/多语言 |
| parallel-enhancement-batch.md | ~8 KB | 批次/P0/P1/P2/并行 |

---

## 使用统计追踪

 auditor S5.7 追踪以下指标：

```json
{
  "layer_usage": {
    "A": { "used": 0, "degraded": 0 },
    "B": { "used": 0, "degraded": 0 },
    "C": { "used": 0, "degraded": 0 },
    "D": { "used": 0, "degraded": 0 },
    "E": { "used": 0, "degraded": 0 },
    "F": { "used": 0, "degraded": 0 },
    "G": { "used": 0, "degraded": 0 },
    "H": { "used": 0, "degraded": 0 },
    "I": { "used": 0, "degraded": 0 },
    "J": { "used": 0, "degraded": 0 },
    "K": { "used": 0, "degraded": 0 },
    "L": { "used": 0, "degraded": 0 },
    "M": { "used": 0, "degraded": 0 },
    "N": { "used": 0, "degraded": 0 }
  },
  "consecutive_clean_audits": 0
}
```
