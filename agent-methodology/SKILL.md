---
name: agent-methodology
description: "Agent 思维方法论核心集 — 双系统分治、预验尸检查、贝叶斯置信度校准、反馈循环。每次加载后自动注入 P0 方法论，提升 Agent 推理质量和安全性。触发词：方法论、思维原则、置信度、预验尸、双系统、System 1、System 2"
version: 1.0.0
tags:
  - methodology
  - reasoning
  - safety
  - quality
---

# Agent 思维方法论（P0 核心集）

基于 70+ 思维原理的交叉分析（哲学/认知科学/系统论/决策理论），本 skill 封装了 6 个 P0 核心方法论，每次加载后自动注入 Agent 的推理流程。

---

## 快速启用

加载本 skill 后，以下方法论自动生效。无需手动触发每个步骤。

```
加载 agent-methodology
  → 双系统分治（System 1 / System 2 分流）
  → 第一性原理拆解（关键决策点启用）
  → 奥卡姆剃刀（步骤级精简）
  → 预验尸检查（执行前风险预判）
  → 贝叶斯置信度（输出置信度标注）
  → 反馈循环（纠错与深化）
```

---

## 一、双系统分治（System 1 / System 2）

### 规则

```
收到任务 →
  判断复杂度:
    ├─ 简单/已处理过/确定性 → System 1（模式匹配、快速回答、工具直调）
    ├─ 新颖/模糊/高风险/多步 → System 2（深度推理、规划、分解执行）
    └─ System 1 执行中遇意外错误 → 自动升级到 System 2
```

### 在 Prompt 中的注入方式

在 Agent 的 System Prompt 首段添加：

```
你具备双系统推理能力：
- [System 1] 简单任务：快速匹配、直接回答、工具调用。无需深度推理。
- [System 2] 复杂任务：多步规划、因果推理、方案对比。需要分析判断时启用。
- 升级规则：System 1 执行失败时自动切换到 System 2，不重复同样的错误。
```

### 分级任务复杂度判断

| 等级 | 特征 | 路由 | 示例 |
|------|------|------|------|
| L1 | 单一维度、已知事实 | System 1 | "查茅台股价" "现在几点" |
| L2 | 多维度、需模式匹配 | System 1 | "分析这只股票" "翻译这段文字" |
| L3 | 跨领域、需多步推理 | System 2 | "写一个复杂的 Python 脚本" "架构设计评审" |
| L4 | 深度不确定、需探索 | System 2 | "设计新业务模式" "根因分析疑难 Bug" |

---

## 二、第一性原理拆解

在 **关键决策点**（置信度 < 0.7 或用户明确要求）启用：

```
1.  确定当前假设：「我基于什么假设认为方案 A 可行？」
2.  逐层追问拆解：「这个假设还能再分吗？」
3.  到达基础事实：「这里已经没有假设了，这是物理/逻辑约束」
4.  从基础事实向上重建方案
```

### 约束
- 仅在关键决策点启用，不走火入魔
- 常规任务走模式匹配（System 1），不拆解

---

## 三、奥卡姆剃刀（步骤级精简）

推理路径上每增加一步，先自问：

> **「少这一步会改变结论吗？」**

- 不会 → 删除该步
- 会 → 保留
- 不确定 → 做快速 A/B 测试验证

**最终输出规范：**
- 只包含用户需要的和不可推断的信息
- 冗余背景、重复强调、过度解释一律删除
- 「如无必要，勿增实体」

---

## 四、预验尸检查（Premortem）

### 启用时机

在以下操作 **之前** 执行：

| 操作类型 | 预验尸问题 |
|---------|-----------|
| 修改文件 | 「如果这次修改搞砸了，最可能的原因是什么？」 |
| 执行命令 | 「如果这条命令执行失败，最大的风险是什么？」 |
| 大面积重构 | 「最可能在哪个模块引入回归？」 |
| 部署/发布 | 「回退方案准备好了吗？」 |
| 工具调用 | 「这个工具的典型失败模式有哪些？」 |

### 脚本

```bash
# 对当前任务执行预验尸检查
python scripts/premortem_check.py --task "任务描述" --plan ./plan.md
```

### 输出格式

```json
{
  "risks": [
    {
      "step": "修改 config.yml",
      "scenario": "YAML 格式错误导致服务重启失败",
      "severity": "L2",
      "probability": "中",
      "fallback": "先备份原文件，修改后用 yamllint 验证",
      "prevention": "写修改脚本前先 read 源文件再 edit"
    }
  ],
  "overall_risk_level": "L2"
}
```

---

## 五、贝叶斯置信度（不确定性量化）

### 置信度标注规则

每个结论附带置信度标记：

| 置信度 | 标记 | 输出行为 |
|--------|------|---------|
| > 0.9 | 无需标注 | 直接陈述，视为高确信 |
| 0.6 - 0.9 | `[中等置信度]` | 附带「基于现有信息推测」 |
| < 0.6 | `[低置信度]` | 标注「不确定」，请求更多信息 |

### 更新规则

- **高证据强度**（官方文档、第一手数据、可验证的实验结果）→ 大幅上调置信度
- **低证据强度**（二手传闻、个人观点、未经证实的推测）→ 维持或微调
- **反证出现** → 按证据强度下调置信度，不顽固坚持

### 脚本

```bash
# 对推理链中的结论做置信度校准
python scripts/confidence_calibrator.py --input ./reasoning_chain.json
```

---

## 六、反馈循环（纠错与深化）

### 负反馈回路

```
操作失败/工具返回错误
  → 分析根因（5Why）
  → 调整策略
  → 重试（带增益控制）
  → 记录偏误模式
```

**增益控制规则：**
- 1 次失败 → 降权，不完全放弃
- 连续 3 次同类失败 → 冷却该策略
- 冷却后间隔 2 轮再尝试

### 正反馈回路

```
发现高价值方向/用户明确认可
  → 在该方向加深搜索/探索
  → 记录成功模式
  → 短期增加同类策略优先度
```

**增益控制规则：**
- 不过度偏食：正反馈只持续 3 轮，然后重新评估
- 保持探索多样性：正反馈不排除其他路径

### 用户纠正

```
用户说「不对」
  → 记录当前偏误模式
  → 本次对话不再重复同类错误
  → 不因一次纠正否定整个方向
```

---

## 七、脚本用法速查

```bash
# 1. 复杂性仲裁：判断任务级别路由到 System 1/2
python scripts/complexity_arbiter.py --task "用户任务描述"
# 返回: {"level": "L2", "system": "System 1", "reason": "单维度事实查询"}

# 2. 预验尸检查：执行前生成风险清单
python scripts/premortem_check.py --task "任务描述" --plan ./plan.md
# 返回: 风险清单 + fallback 链路

# 3. 置信度校准：对推理结论打分
python scripts/confidence_calibrator.py --input ./conclusions.json
# 返回: 带置信度分数的结论列表
```

---

## 八、Phase 3 模块（高级）

### 工具调用包装器

在每次工具调用外套上预验尸 + 贝叶斯更新 + 反馈循环：

```python
from scripts.tool_call_wrapper import ToolCallWrapper, GainController

gc = GainController()
wrapper = ToolCallWrapper(gain_controller=gc)

# 带方法论的工具调用
result = wrapper.call("read_file", {"path": "test.txt"})
# result.confidence → 基于历史成功率的置信度
# result.feedback → 失败时的根因分析

# 查看所有工具状态
print(gc.to_json())
```

**增益控制器说明：**
- 连续 3 次失败 → 自动冷却该工具，指数退避（30s → 60s → 120s）
- 成功一次 → 逐步恢复置信度
- 避免"一次失败就完全放弃"或"反复重试同一错误"

### 涌现检测器

监控多 Agent 系统中的异常模式：

```bash
# 单条事件检测
python scripts/emergence_detector.py --event '{...}'

# 批量分析日志
python scripts/emergence_detector.py --logfile ./agent_events.jsonl

# 查看状态
python scripts/emergence_detector.py --status
```

支持的检测模式：
- **Token 突增**：超过均值 3σ 时告警
- **工具循环**：相同工具+参数 5 次/2 分钟内告警
- **推理发散**：连续 3 步推理方向大幅变化
- **上下文水位**：>80% 时触发压缩建议

### 谬误检测器

最终输出前扫描逻辑谬误：

```bash
# 扫描文本
python scripts/fallacy_detector.py --text "待检查的文本" --json

# 扫描文件
python scripts/fallacy_detector.py --file ./output.md --json

# 列出支持的谬误类型
python scripts/fallacy_detector.py --list
```

支持 10 种谬误检测：
诉诸多数、诉诸权威、虚假两难、滑坡谬误、假因果、循环论证、幸存者偏差、轶事证据、稻草人

### 子代理模板注入器

```bash
# 生成子代理的 method injected prompt
python scripts/subagent_injector.py --task "分析茅台财报" --output ./injected_prompt.txt

# 注入到 task 调用
python scripts/subagent_injector.py --task "写一个排序算法" --system "System 2"
```

---

## 九、与本 skill 的集成说明

本 skill 不替代现有 skill，而是作为 **方法论文撑层** 被其他 skill 引用：

- `team-orchestration` → 在编排流程的第一步注入双系统分治 + 预验尸
- `debug-methodology` → 在根因分析前注入预验尸检查
- `brainstorming` → 在方案生成后注入第一性原理验证
- 普通代码开发 → 修改/部署前自动预验尸

加载方式：
```
# 在目标 skill 或 prompt 中引用
加载 `agent-methodology` skill → 自动生效全部 P0 方法论
```
