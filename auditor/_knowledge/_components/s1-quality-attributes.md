# S1-QA 质量属性检查（增强层K）

> 注入点：Phase-S S1（战略评估）
> 触发方式：按条件激活
> 输出：qa_results + qa_risk_adjustment

---

## 与 S5.6 的边界定义

| 维度 | S1-QA（前置审计） | S5.6（事后建议） |
|------|------------------|-----------------|
| 多线程 | 是否使用并行模式（存在性） | 并行优化建议（质量） |
| Token | Token预算/Context精简（架构） | Token节省技巧（执行） |
| 模型调用 | 调用链路是否最短（结构） | 调用优化建议（性能） |

---

## QA1 — 工作流合理性【始终激活】

**触发条件**：Phase-G 分类为 Agent变更/Skill变更 且涉及工作流设计

**检查内容（6项）**：
| # | 检查项 | 标准 |
|---|--------|------|
| 1 | 流程完整性 | 是否有遗漏的关键步骤 |
| 2 | 步骤顺序合理性 | 依赖关系是否正确 |
| 3 | 并行机会识别 | 独立步骤是否可并行 |
| 4 | 串行瓶颈识别 | 是否有不必要的串行等待 |
| 5 | 异常处理完备性 | 关键节点是否有错误处理 |
| 6 | 人机交接点 | 需用户确认的节点是否明确 |

**评级**：pass≥6项 / warn 4-5项 / fail <4项

---

## QA2 — 多线程使用检查【按需激活】

**触发条件**：Phase-G 分类含「跨Agent协议」或「并行任务」

**检查内容（5项）**：
| # | 检查项 | 标准 |
|---|--------|------|
| 1 | 并行标识 | 可并行任务是否标注 `parallel` |
| 2 | 隔离性 | 并行任务workspace/环境变量是否隔离 |
| 3 | 同步点 | 汇合点是否定义清晰 |
| 4 | 冲突风险 | 共享资源是否有互斥保护 |
| 5 | 加速比 | 并行收益>并行开销 |

**评级**：pass5项 / warn 3-4项 / fail <3项 / n/a不满足触发条件

---

## QA3 — 降级机制检查【按需激活】

**触发条件**：Phase-G 分类含「系统变更」且含 fault-tolerant 设计

**检查内容（5项）**：
| # | 检查项 | 标准 |
|---|--------|------|
| 1 | 触发条件定义 | 降级触发条件是否明确 |
| 2 | 降级路径存在 | 降级后是否有fallback方案 |
| 3 | 功能损失说明 | 降级后功能损失是否可接受 |
| 4 | 可测试性 | 降级路径是否可独立测试 |
| 5 | 恢复机制 | 是否支持从降级状态恢复 |

**评级**：pass5项 / warn 3-4项 / fail <3项 / n/a

---

## QA4 — Token 消耗审计【按需激活】

**触发条件**：任意含模型调用或 Context 操作的变更

**检查内容（5项）**：
| # | 检查项 | 标准 |
|---|--------|------|
| 1 | Token预算设定 | 是否有单次/日均/总量上限 |
| 2 | Context精简 | SKILL.md/rules.md是否精简（核心<1500 token） |
| 3 | 压缩策略 | 超长Context是否有压缩方案 |
| 4 | 缓存/batch | 高频调用是否有缓存或批量优化 |
| 5 | 浪费检测 | 是否有重复加载同一内容 |

**评级**：pass5项 / warn 3-4项 / fail <3项 / n/a

---

## QA5 — 模型调用次数检查【按需激活】

**触发条件**：任意含模型调用或 API 封装的变更

**检查内容（5项）**：
| # | 检查项 | 标准 |
|---|--------|------|
| 1 | 调用链路最短 | 路由设计是否最短 |
| 2 | 去重检测 | 同一数据是否被多次请求 |
| 3 | 多模型优化 | 多模型场景下路由是否最优化 |
| 4 | 重试机制 | 失败重试是否有退避策略 |
| 5 | 调用计数 | 是否有可观测的调用计数 |

**评级**：pass5项 / warn 3-4项 / fail <3项 / n/a

---

## 风险等级调整规则

| QA fail 数 | 调整幅度 | 说明 |
|------------|---------|------|
| 0 | 不变 | 无fail |
| 1 | +0.5级（向上取整） | 有风险 |
| >=2 | +1级（上限L4） | 高风险 |

---

## 输出格式

```json
{
  "qa_results": {
    "workflow_rationality": {"status": "pass|warn|fail", "score": "X/6", "findings": [], "recommendations": []},
    "multi_threading": {"status": "pass|warn|fail|n/a", "score": "X/5", "findings": [], "recommendations": []},
    "degradation": {"status": "pass|warn|fail|n/a", "score": "X/5", "findings": [], "recommendations": []},
    "token_consumption": {"status": "pass|warn|fail|n/a", "score": "X/5", "findings": [], "recommendations": []},
    "model_api_calls": {"status": "pass|warn|fail|n/a", "score": "X/5", "findings": [], "recommendations": []}
  },
  "qa_summary": {
    "total_checks": 5, "passed": 0, "warnings": 0, "failed": 0, "na": 0
  },
  "qa_risk_adjustment": {
    "original_risk": "L2", "adjusted_risk": "L3", "fail_count": 1, "reason": "..."
  }
}
```