# auditor 自学习与事实核查

## 自学习机制

### 触发条件

| 条件 | 阈值 | 来源 |
|------|:----:|------|
| 同一类别变更失败 | ≥3 次 | 失败记录 |
| Q-Gate 失败率 | >20% | 失败分析 |
| 子代理超时率 | >30% | 超时记录 |
| 审计新型 | 发现新型 | G1 分类结果 |

### S5.9 进化引擎流程

```
同一类别变更=3次失败记录
  → 本地进化：self-improving-agent → 更新技能自优化
  → 社区进化：≥3次同类 → 上报 capability-evolver
  → 结果：技能自改进 + 社区知识库更新
```

### 经验归档流程

```
记录（Recording）→ 分类 → 泛化 → 归档 → 应用
```

### 经验文件

| 文件 | 用途 |
|------|------|
| `_knowledge/_refined/LEARNINGS.md` | 经验精化记录 |
| `_knowledge/_index/keyword-index.md` | 关键词索引 |
| `_knowledge/_index/topic-index.md` | 主题索引 |
| `_knowledge/core-principles/auditor-principles.md` | 核心原则 |
| `_knowledge/references/external/auditor-expert-knowledge.md` | 外部专家知识 |

### 经验核查原则

每次经验归档需经过：
1. **P1 先读再改**：确认读取了相关规则和上下文
2. **P2 不准假装测试通过**：经验必须有实际案例支撑
3. **P3 不准加不需要的功能**：只标记已发生案例
4. **P4 先简后复**：从具体案例泛化通用规则
5. **P5 不准过度封装**：描述保持透明可读

## 事实核查

每次审计完成、返回结果前必须调用共享事实核查工具。

```python
import sys
from pathlib import Path
fact_check_path = Path.home() / ".qclaw" / "skills" / "_shared" / "fact-checker"
sys.path.insert(0, str(fact_check_path))

from fact_check import fact_check
result = fact_check(
    task_description="...",
    execution_summary="...",
    output_claims=["变更已审查", "风险等级L2"],
    skill_context={"skill": "auditor", "complexity": "T3"},
    source_claims=[
        {
            "file": "D:/my_project/src/core/backtest_engine.py",
            "description": "_check_sell_signals 有 date 可用性检查",
            "expected_find": "if c not in funds_data or d not in funds_data[c].index",
        },
    ],
    base_dir=".",
)
```

### 核查标准

| 维度 | 检查内容 |
|------|---------|
| 完整性 | Phase-G 所有步骤是否完成？报告是否完整？ |
| 准确性 | 风险等级/变更类型/增强层判断是否准确？ |
| 代码准确性 ⚠️ | 涉及文件+行号的结论与源文件一致？|
| 边界 | 是否在 auditor 技能范围内？ |
| 一致性 | 执行过程是否按审计流程（Phase-G + S1-S5）？ |

| 结果 | 处理 |
|:----:|------|
| PASS | 直接返回审计报告 |
| WARN | 返回报告 + 标注待确认项 |
| FAIL | 不返回报告，先修复再返回 |

> **强制规则**：source_claims 中任何一条验证失败 → fact_check 返回 FAIL。代码声明未经验证严禁输出。

工具路径：`_shared/fact-checker/fact_check.py`

## 优化模块

| 模块 | 文件 | 功能 |
|------|------|------|
| 知识缓存 | `scripts/knowledge_cache.py` | 知识文件内存缓存，I/O 减少 90%+ |
| 质量检查并行 | `scripts/parallel_quality_checks.py` | Q0-Q7 并行执行，加速 4-5 倍 |

### 知识缓存使用

```python
from knowledge_cache import load_knowledge_cached
content = load_knowledge_cached("core-principles/audit-principles.md")
from knowledge_cache import clear_knowledge_cache
clear_knowledge_cache()
```

### 质量检查并行使用

```python
from parallel_quality_checks import run_parallel_quality_checks
report = run_parallel_quality_checks(skill_dir="~/.qclaw/skills", target_skill="auditor")
print(report.summary())
```