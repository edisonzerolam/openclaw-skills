# agent-planner 自学习与事实核查

## 自学习机制

### 触发条件

| 场景 | 动作 | 更新文件 |
|------|------|---------|
| 规划任务完成 | 记录执行摘要 | `_knowledge/_refined/LEARNINGS.md` |
| 新坑点发现 | 追加到坑点库 | `_knowledge/_enhancement/pitfall-library.md` |
| 专家知识注入 | 更新知识库 | `_knowledge/references/external/agent-planner-expert-knowledge.md` |
| 新主题/关键词 | 更新索引 | `_knowledge/_index/keyword-index.md`, `topic-index.md` |
| 核心原则修正 | 更新原则文件 | `_knowledge/core-principles/agent-planner-principles.md` |
| 版本演进 | 更新演进记录 | `_knowledge/_enhancement/plan-tracker/evolution-log.md` |

### 更新优先级

| 优先级 | 类型 | 周期 |
|:------:|------|:----:|
| P0 | 新坑点 | 立即 |
| P1 | 任务完成 | 每次 |
| P2 | 专家知识 | 定期批量 |
| P3 | 索引/原则 | 按需 |

### 记录格式

```markdown
### YYYY-MM-DD HH:mm
**触发任务**: [描述]
**执行动作**: [做了什么]
**学习成果**: [学到了什么]
**更新文件**: [文件列表]
```

### 版本管控

- 自学习触发时版本号递增
- LEARNINGS.md 记录所有事件（禁止删除历史）
- 核心原则变更标注来源

## 事实核查

每次执行完成、返回结果前必须调用共享事实核查工具。

```python
from fact_check import fact_check
result = fact_check(
    task_description="...",
    execution_summary="...",
    output_claims=["规划方案已完成", "影响文件N个"],
    skill_context={"skill": "agent-planner", "complexity": "T3"},
    source_claims=[
        {
            "file": "path/to/file.py",
            "description": "函数foo存在日期边界检查",
            "expected_find": "if date < start_date",
        }
    ],
    base_dir="."
)
```

| 结果 | 处理 |
|:----:|------|
| PASS | 直接返回规划方案 |
| WARN | 返回方案 + 标注待验证项 |
| FAIL | 不返回，先修复再返回 |

工具路径：`_shared/fact-checker/fact_check.py`

## 优化模块

| 模块 | 文件 | 功能 |
|------|------|------|
| 知识缓存 | `scripts/knowledge_cache.py` | 知识文件内存缓存，I/O 减少 90%+ |
| 子代理直连 | `scripts/spawn_agent_direct.py` | 绕过 PowerShell 中转，延迟降低 75% |

### 知识缓存使用

```python
from knowledge_cache import load_knowledge_cached
content = load_knowledge_cached("core-principles/planning-principles.md")
from knowledge_cache import clear_knowledge_cache
clear_knowledge_cache()
```

### 子代理直连使用

```python
from spawn_agent_direct import spawn_agent_direct
result = spawn_agent_direct(task="审查 backtest_engine.py 默认参数...", label="engine-auditor", mode="run")

from spawn_agent_direct import spawn_agents_parallel
results = spawn_agents_parallel(
    tasks=["任务1", "任务2", "任务3"],
    labels=["expert-1", "expert-2", "expert-3"]
)
```