# debug 自学习与事实核查

## 事实核查

每次技能执行完成、返回结果前，必须调用共享事实核查工具。

```python
from fact_check import fact_check
result = fact_check(
    task_description="...",
    execution_summary="...",
    output_claims=["claim1", "claim2"],
    skill_context={"skill": "debug", "complexity": "T3"},
    source_claims=[
        {
            "file": "path/to/file.py",
            "description": "函数foo存在日期边界检查",
            "expected_find": "if date < start_date",
        }
    ],
    base_dir=".",
)
```

| 结果 | 处理 |
|:----:|------|
| PASS | 直接返回结果 |
| WARN | 返回 + 标注已知问题 |
| FAIL | 不返回，先修复再返回 |

工具路径：`_shared/fact-checker/fact_check.py`

## 自学习

每次 debug 执行后，将经验写入 `_knowledge/_refined/LEARNINGS.md`：

```markdown
### [触发词/场景关键词]
- **任务**：<一句话>
- **关键决策**：<为什么这样做>
- **结果**：<成功/失败/学到什么>
- **索引关键词**：<3-5 个可搜索词>
```

加载时机：SKILL.md 后立即检查 `_refined/LEARNINGS.md`，按触发词匹配。

## 跨 skill 错误模式反馈

debug 发现的新错误模式写入本地 LEARNINGS.md：

```
debug 执行 → 发现新模式（不在 knowledge-error-patterns.md 中）
  → 写入 debug/_knowledge/_refined/LEARNINGS.md
  → agent-planner F7 阶段只读引用
```

agent-planner F7 引用路径：`~/.qclaw/skills/debug/_knowledge/_refined/LEARNINGS.md`

> **注意**：仅写入本 skill 的 LEARNINGS.md，不跨 skill 写入。