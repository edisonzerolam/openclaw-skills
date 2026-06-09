# auditor 执行框架（S1-S5 详细）

## S1 — 战略评估

**输入**：Phase-G + workspace
**输出**：影响范围 + L1-L4 风险 + 财务合规层（如适用）

### 8 项准考察（完成任意 4 项即可推进）

1. 影响范围
2. 风险等级（L1-L4）
3. 变更细节
4. 变更来源
5. 变更路径
6. E5 备选
7. E6 来源
8. 质量属性检查

### 增强层 K — 质量属性（按需激活）

| QA 等级 | 触发条件 | 检查项数 |
|:-------:|---------|:--------:|
| QA1 工作流 | Agent/Skill 变更 + 工作流设计 | 6 |
| QA2 多线索 | 跨 Agent/并行任务 | 5 |
| QA3 降级 | 系统变更 + 架构错误设计 | 5 |
| QA4 Token | 模型调用/Context 操作 | 5 |
| QA5 模型调用 | API 封装/模型调用 | 5 |

QA fail=0 → 风险不变；fail=1 → +0.5 级；fail≥2 → +1 级（上限 L4）
详见 `_knowledge/_components/s1-quality-attributes.md`

### 增强层 L — 财务合规层

当 G1=`财务合规审计` 时额外执行：
1. 定义审计范围（财务/运营/IT/内控）
2. 确立审计目标（准确性/合规性/风险/效率）
3. 设定重要性阈值（materiality threshold）
4. 识别适用准则（GAAP/IFRS/企业政策）
5. 关联增强层 L（加载领域知识）

详见 `_knowledge/_components/financial-compliance.md`

## S2 — 规划合并与子代理

**输入**：Q1 行 / 有并行潜力
**输出**：JSON 规划文档

- 参考 `_knowledge/_components/session-manager.md`
- 增援层 D/H 辅助
- 子代理派发使用 `sessions_spawn`（agent-team spawn 已废弃）

## S3 — 合并审核

### S3a 预检（S4 前）
- Tier-1 完整
- 坟点≤3
- 降级策略完整
- 异常处理存在

### S3b Merge Gate（S4 后）
- S2 未正式提交 → 阅 S2
- 正式 fail → 修改/阅 S4
- 非正式 fail → 修改/阅 S4（记录到 S5）
- 通过 → 通过

### S3c Review Loop（限 3 次迭代 R0/R1/R2）

S3b 发现 P0/P1 fail 时触发。

```
S3c.1 收集 fail 项 → 写入 audit_review_queue
S3c.2 派发子代理修复 → [SG1 门禁] → 通过后进入 S3c.3
S3c.3 验证修复充分性（逐项检查修复报告+文件）
S3c.4 回归 S3b → [SG2 门禁] → 通过→S5，未通过→迭代+1
checkpoint: S3c.4 后写入 _checkpoints/
```

**SG1 门禁**（S3c.2→S3c.3）：
- SG1.1: P0 清零
- SG1.2: P1 修复率≥80%
- SG1.3: 子代理成功率≥60%
- SG1.4: 无新增 P0

**SG2 门禁**（S3c.4→S5）：
- SG2.1: P0=0
- SG2.2: 新 P1≤3
- SG2.3: 等级升级需书面理由
- SG2.4: 验证记录完整

**超时恢复**：全部子代理超时（0%成功率）→ 强制降级主会话（mandatory_override=True）
详见 `_knowledge/_enhancement/subagent-timeout-recovery.md`

### 财务合规层（S3 嵌入）
- 审计证据链完整性核查
- 风险映射：High/Medium/Low
- 合规准则对照：GAAP/IFRS/企业政策

## S4 — 执行与验证

### E5 备选（L3+ 强制）
```bash
git add -A && git commit -m "audit-backup-{YYYYMMDD}-{seq}"
```

### 8 项验证（L3+ 强制，L1/L2 可选）
文件存在 / 数据一致 / 资源标识 / 路径 / 编辑 / 前置结果 / 版本

可 asyncio 并行，约 0.32x 加速。

### S4.5 — 代码实读验证（强制步骤）

> 审计报告中任何涉及具体文件/行号的结论，必须逐条读取源文件验证后再输出。

**触发条件**（满足任一）：
- 涉及文件名+行号
- 声称某代码"存在"或"缺失"某特征
- "A 版已修复但 B 版未修复"
- 多版本对比结论

**验证方式**：

```python
from fact_check import verify_source_claims

source_claims = [
    {
        "file": "D:/my_project/src/core/backtest_engine.py",
        "description": "CPU _check_sell_signals 有 date 可用性检查",
        "expected_find": "if c not in funds_data or d not in funds_data[c].index",
        "line_hint": 381,
    },
]

verifications = verify_source_claims(source_claims, base_dir=".")
for v in verifications:
    if not v.verified:
        print(f"MISREPORT: {v.description} → {v.evidence}")
```

**验证规则**：
1. CPU/GPU 各自独立验证，禁止对称推断
2. 行号匹配 ≠ 内容一致，必须 grep 确认
3. 只要一条 source_claim 验证失败 → 审计结论必须修正

## S5 — 结果归档

| 子步骤 | 要点 |
|--------|------|
| S5.5 循环限制 | 迭代>2 次 pending 自审/Artifact 逾越→退出 |
| S5.6 性能优化建议 | 模型/Token/多线索（事后建议）|
| S5.7 增强层统计 | A-L 使用次数 + 连续 clean 次数 |
| S5.8 失败路径 | 降级>50% → 触发优化建议 |
| S5.9 进化引擎 | self-improving + capability-evolver（≤3 次同类）|
| S5.10 经验写入 | `_knowledge/_refined/LEARNINGS.md` |
| S5.11 修复对象输出 | 审计完成后输出修复后完整文件（仅单一文件审计适用）|

### S5.11 — 修复对象输出

| 子节点 | 输入 | 输出 |
|--------|------|------|
| O1 识别修复范围 | 审计结果 | 修复清单 |
| O2 生成修复对象 | 原文件+修复清单 | `_auditor_output/{原文件名}.fixed.{ext}` |
| O3 S5-FIXED-GATE | O2 产出 | 通过/不通过 |
| O4 输出交付 | O3 通过 | 路径+diff+免责声明 |

**S5-FIXED-GATE 7 项检查**：
1. 修复完整性（每个审计发现都有对应修复）
2. 审计范围对齐（修复不超出原范围）
3. E5 备份已执行
4. 无新问题引入
5. 语法检查（`python -m py_compile`）
6. 导入测试（`python -c "import <module>"`）
7. 冒烟测试（单次调用无异常）

**不适用场景**：目录结构/架构/系统配置审计、财务合规审计、clean audit（自动跳过）
**安全机制**：以 `.fixed` 新文件名输出，不替换原文件