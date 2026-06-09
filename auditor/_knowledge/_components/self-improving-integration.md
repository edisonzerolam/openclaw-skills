# S5.9 自我进化引擎集成

> 版本：v1.0 | 状态：active
> 来源：auditor v6.2 S5.9 增强层 G
> 定位：S5 结尾的双引擎分发协议

---

## 双引擎定位

| 引擎 | 定位 | Skill | 触发条件 |
|------|------|-------|---------|
| **self-improving-agent** | 本地经验级进化 | 独立Skill | 日常经验积累，模式提取 |
| **capability-evolver** | 跨Agent社区进化 | 独立Skill | 需要外部基因库，同类问题≥3次 |

---

## S5.9 分发流程

```
S5 收尾审计完成
    ↓
判断：本次审计是否产生可复用的进化知识？
    ├── 否 → 跳过进化，仅记录审计结果
    └── 是 → 触发进化分发判断
                ↓
        判断：是否需要跨Agent社区经验？
            ├── 是（同类问题出现≥3次）→ capability-evolver
            └── 否（首次/偶发问题）→ self-improving-agent
                ↓
        结果沉淀到 Layer2 frozen_version.json
```

---

## 引擎A：self-improving-agent（本地）

### 输入（来自 auditor S5）

| 字段 | 说明 | 示例 |
|------|------|------|
| `audit_type` | 审计类型 | skill_modification / financial_audit |
| `issues_found[]` | 发现的问题 | P0/P1/P2 列表 |
| `optimizations[]` | 优化建议 | Token节省/流程改进 |
| `layer_used[]` | 使用的增强层 | [A,B,L] |
| `degraded_layers[]` | 降级增强层 | 降级原因 |
| `consecutive_clean` | 连续干净审计数 | 3 |

### 输出沉淀格式

```yaml
# 更新 memory/semantic-patterns.json
patterns:
  auditor_pattern_{date}_{seq}:
    id: auditor_pattern_{YYYY-MM-DD}_{seq}
    source: auditor_self_improvement
    confidence: 0.85
    applications: 1
    created: "{YYYY-MM-DD}"
    category: auditor_optimization
    pattern: "{一句话模式描述}"
    problem: "{什么问题被解决}"
    solution: "{auditor是如何做的}"
    quality_rules: ["{优化建议1}", "{优化建议2}"]
    target_skills: ["auditor"]
```

---

## 引擎B：capability-evolver（社区）

### 调用方式

```bash
# 1. 搜索现有基因（是否已有同类解决方案）
POST http://127.0.0.1:19820/asset/search
{"signals": ["auditor_optimization", "{issue_category}"], "mode": "semantic", "limit": 5}

# 2. 如果需要，提交本次审计的进化经验为新基因
POST http://127.0.0.1:19820/asset/submit
{"assets": [{"type": "Gene", "content": "{auditor_pattern_yaml}"}]}

# 3. 轮询提交结果
POST http://127.0.0.1:19820/mailbox/poll
{"type": "asset_submit_result"}
```

### 触发条件（严格）

| 条件 | 说明 |
|------|------|
| 同类问题出现≥3次 | 跨多次审计的同类P0/P1 |
| 问题属于通用架构 | 非特定Skill的系统性问题 |
| self-improving-agent置信度≥0.8 | 模式已验证 |
| 用户明确要求 | 用户说"分享到社区"/"上报Hub" |

---

## 结果沉淀（两者共同）

1. **Layer2 frozen_version.json**：
   ```json
   {
     "consecutive_clean_audits": {n},
     "last_evolution": "{YYYY-MM-DD}",
     "evolution_engines": {
       "self_improving": { "last_used": "...", "patterns_added": n },
       "capability_evolver": { "last_used": "...", "genes_submitted": n }
     }
   }
   ```

2. **behavior-institutionalization 违规记录**（如有P0/P1违规）

---

## Fallback

| 场景 | Fallback |
|------|----------|
| self-improving-agent 未安装 | 降级为手动模式，S5结果仅写入frozen_version.json |
| capability-evolver Proxy不可达 | 跳过社区上报，提示"Hub离线，仅本地记录" |
| 两者都不可用 | S5正常完成，进化步骤静默跳过，不阻塞审计 |