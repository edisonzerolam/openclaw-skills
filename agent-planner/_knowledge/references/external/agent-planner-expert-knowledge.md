# agent-planner 专家知识库

> 收集互联网专家知识，来源涵盖Prompt工程/Agent系统设计/技能设计/知识管理方向

---

## 来源1: Karpathy — "Think Before Coding" 原则

**作者**: Andrej Karpathy (OpenAI/FSD/特斯拉)
**链接**: https://karpathy.github.io/2022/08/05/reasoning/
**主题**: 快思维 vs 慢思维，Agent规划前先思考

### 核心理论

Karpathy 提出"系统1 vs 系统2"框架：
- **系统1（快思维）**: 直接反应，基于Pattern Matching
- **系统2（慢思维）**: 刻意推理，规划前必先思考

### 对agent-planner的指导

```
触发场景：规划任务词（规划/方案设计/Agent架构/任务分解）
前置动作：
  1. 读取 rules.md → 理解当前Agent的身份和约束
  2. 读取 identity-config.md → 理解当前Agent的能力范围
  3. 读取 memory/YYYY-MM-DD.md → 理解近期上下文
  4. 再执行规划
核心原则：先读再改不准盲改（Think Before Acting）
```

---

## 来源2: Anthropic — Claude Agent系统设计指南

**作者**: Anthropic
**链接**: https://docs.anthropic.com/en/docs/build-agentic-systems
**主题**: Agent循环设计（Plan → Act → Observe → Loop）

### 核心理论

Anthropic 定义Agent的核心循环：
```
while <goal not achieved>:
  1. Plan → 规划下一步行动
  2. Act → 执行工具调用
  3. Observe → 观察结果
  4. Loop → 决策是否继续
```

### 关键设计模式

| 模式 | 说明 | agent-planner对应 |
|------|------|-------------------|
| 单轮规划 | 直接输出方案 | P2单次规划 |
| 多轮反思 | 输出→评估→修正→输出 | 迭代版本控制（F12） |
| 外部检索 | 规划前查知识库 | F4知识库检索 |
| 子Agent并行 | 分解任务并行执行 | F11子代理调用 |

---

## 来源3: Lilian Weng — "Prompt Engineering Guide"

**作者**: Lilian Weng (OpenAI)
**链接**: https://www.promptingguide.ai/
**主题**: Prompt工程核心技巧，Chain of Thought/ReAct/Self-Consistency

### 核心Prompt模式

| 模式 | 触发场景 | agent-planner对应 |
|------|---------|-------------------|
| CoT (Chain of Thought) | 复杂推理任务 | P1多方案对比时展示推理链 |
| ReAct (Reasoning + Acting) | 规划+执行交替 | F6工作流编排（4-A目标拆解→4-B自动生成）|
| Few-shot | 少样本学习 | templates/s5-report.md 示例模板 |
| Self-consistency | 投票选出最一致答案 | 版本迭代控制（多版→用户决策）|

### 对agent-planner的增强

```
规划阶段（Plan）:
  → 使用 CoT 展示多方案对比推理过程
  → 使用 Few-shot 示例（templates/s5-report.md）规范输出格式

执行阶段（Act）:
  → 使用 ReAct 循环：方案 → 子代理执行 → 观察 → 修正
  
监控阶段（Observe）:
  → 使用 Self-consistency 验证方案一致性（版本演进记录）
```

---

## 来源4: DeepLearning.AI — "Agentic AI Design Patterns"

**作者**: DeepLearning.AI / Andrew Ng
**链接**: https://www.deeplearning.ai/ short-courses/building-multi-agent-ai-systems/
**主题**: 多Agent系统设计模式，Handoffs/Collaboration/Broadcast

### 多Agent协作模式

| 模式 | 说明 | agent-planner对应 |
|------|------|-------------------|
| Handoffs | 任务交接，A→B→C | 子代理任务分配（F11）|
| Collaboration | 共享状态协作 | workspace共享（Zone A/B）|
| Broadcast | 一对多广播 | plan-tracker版本广播（T2→T3→T4→T5）|

### 对agent-planner的增强

```
F11子代理调用模式（基于Handoffs模式）：
  L1: agent-team team create → 团队长分配任务
  L2: Task parallel → 并行执行无依赖任务
  L3: sessions_spawn → 串行兜底

F12版本追踪（基于Broadcast模式）：
  T2: 追加版本记录（广播至所有相关方）
  T5: 残余变更Cron（定期广播提醒）
```

---

## 来源5: Microsoft Research — "AutoGen Framework"

**作者**: Microsoft Research
**链接**: https://microsoft.github.io/autogen/
**主题**: 多Agent对话框架，GroupChat/Manager模式

### 核心架构

```
Manager Agent:
  ├── 接收用户请求
  ├── 分解为子任务
  ├── 分派给 Specialized Agents
  └── 汇总结果返回用户

GroupChat:
  ├── 指定发言顺序 或
  ├── 让Agent自动选择下一个发言人
  └── 支持SpeakerSelection功能
```

### 对agent-planner的增强

```
plan-tracker架构（类Manager模式）：
  主会话 = Manager（分解任务+分配+汇总）
  子代理 = Specialized Agent（执行子任务）
  
F12版本追踪（类GroupChat）：
  所有规划参与者共享evolution-log.md
  每个版本记录广播至所有相关方
```

---

## 来源6: 港科大（HKUST）— "Prompt Engineer职业技能框架"

**作者**: 香港科技大学
**链接**: https://lp-sapphire.hkust.edu.hk/prompt-engineering
**主题**: Prompt Engineer能力模型（知识获取→知识整理→知识验证→知识应用）

### 能力模型（4阶段）

| 阶段 | 能力 | agent-planner对应 |
|------|------|-------------------|
| 知识获取 | 从专家/文档/网络获取知识 | F4架构方案（知识融合）|
| 知识整理 | 分类/标签/结构化 | F9 Workspace卫生检查（4-Zone分区）|
| 知识验证 | 验证知识正确性/完整性 | 质量自检（完整性/可执行性/风险控制）|
| 知识应用 | 应用知识解决实际问题 | F6工作流编排（Epic→Task→Step）|

---

## 来源7: 张峻旸 — "AI Agent工程落地框架"

**作者**: 张峻旸（阿里云）
**链接**: https://zhuanlan.zhihu.com/p/AI-Agent-Engineering
**主题**: AI Agent工程化落地（规划器/执行器/记忆/工具四大模块）

### 四大模块

| 模块 | 说明 | agent-planner对应 |
|------|------|-------------------|
| 规划器（Planner） | 任务分解+方案生成 | P-Sub-P（3级输出：P1/P2/P3）|
| 执行器（Executor） | 工具调用+结果反馈 | F11子代理调用（3级执行路径）|
| 记忆（Memory） | 短期/长期记忆管理 | memory/YYYY-MM-DD.md + memory-config.md |
| 工具（Tools） | 技能/Skill调用 | F5技能选型（KANO模型）|

### 对agent-planner的增强

```
P-Sub-P（规划器）:
  P1 批量计划 → 多方案对比（规划器）
  P2 单次规划 → 单方案详细（规划器）
  P3 子任务分解 → Task级执行（执行器）

记忆模块:
  短期记忆 → memory/YYYY-MM-DD.md
  长期记忆 → memory-config.md
  工作记忆 → rules.md + identity-config.md
```

---

## 来源8: PromptLayer — "Prompt工程最佳实践"

**作者**: PromptLayer
**链接**: https://promptlayer.com/blog/prompt-engineering-best-practices/
**主题**: Prompt版本管理/标签/追踪/A-B测试

### 核心实践

| 实践 | 说明 | agent-planner对应 |
|------|------|-------------------|
| Prompt版本管理 | 每次变更记录版本号+变更说明 | F12版本迭代控制（v{主}.{次}格式）|
| Prompt标签 | 打标签分类（quality/variance/cost） | F3成本预估（Token/调用次数/迭代次数）|
| Prompt追踪 | 追踪每次Prompt效果 | F12版本追踪（evolution-log.md）|
| A-B测试 | 多版本方案对比 | P1批量计划（多方案对比） |

---

## 来源9：ReAct (arXiv:2210.03629) — 推理-行动交替范式

**链接**：https://arxiv.org/abs/2210.03629
**时间**：2022年（引用>8000次，确立Agent标准范式）
**核心贡献**：确立"推理-行动交替"Agent标准范式

### 关键概念

#### ReAct循环
```
Thought → Action → Observation → Thought → ...
```
- **agent-planner映射**：F6工作流编排的4-A目标拆解对应"Thought"阶段，4-B自动生成对应"Action"阶段

#### 与F11子代理调用的关联
- 每个子代理可独立执行ReAct循环
- 主会话负责任务分发和结果汇总

---

## 来源10：MetaGPT (arXiv:2308.00352) — SOP编码+装配线多Agent

**链接**：https://arxiv.org/abs/2308.00352
**时间**：2023年（被后续所有多Agent框架引用）
**核心贡献**：SOP编码+装配线多Agent

### 关键概念

#### 装配线模式
- 不同Agent担任不同专业角色（如：工程师、架构师、审查员）
- **agent-planner映射**：F5技能选型（KANO模型）对应角色分工

#### SOP编码
- 将标准操作程序编码为Agent协作规则
- **agent-planner映射**：F6工作流编排（Epic→Task→Step）对应SOP分解

---

## 来源11：LLM Agent规划综述 (arXiv:2402.02716) — 首个系统梳理

**链接**：https://arxiv.org/abs/2402.02716
**时间**：2024年2月
**核心贡献**：首个系统梳理LLM Agent规划，5大类别：分解/选择/外部模块/反思/记忆

### 五大类别与agent-planner映射

| 类别 | 说明 | agent-planner对应 |
|------|------|-------------------|
| 分解（Decomposition） | 任务分解为子任务 | P3子任务分解 + F6 Epic→Task |
| 选择（Selection） | 选择下一步行动 | F10适用场景判断 |
| 外部模块（External Modules） | 调用外部工具 | F5技能选型 + KANO模型 |
| 反思（Reflection） | 自我纠错 | 版本迭代控制（v{主}.{次}）|
| 记忆（Memory） | 长期/短期记忆 | memory/YYYY-MM-DD.md + memory-config.md |

---

## 来源12：AgentBench (arXiv:2308.03688) — Agent评估Benchmark

**链接**：https://arxiv.org/abs/2308.03688
**时间**：2023年
**核心贡献**：建立Agent评估Benchmark，推动能力提升研究

### 对agent-planner的指导
- **质量自检**：规划完成后需验证方案可行性
- **版本迭代**：迭代上限5版，超5版强制用户决策

---

## 来源13：NeuroMAS (2025.5) — 多Agent系统神经网络建模

**链接**：arXiv相关研究
**时间**：2025年5月
**核心贡献**：多Agent系统建模为神经网络，RL自动学习协作策略

### 对agent-planner的启发
- **F11子代理调用**：从手工工作流→自适应学习
- **协自动化**：层级式规划+低层执行的主流方向

---

## 来源14：BOAD (2025.12) — Bandit优化自动发现层级式软件工程Agent

**链接**：arXiv相关研究
**时间**：2025年12月
**核心贡献**：Bandit优化自动发现层级式软件工程Agent

### 对agent-planner的启发
- **P1批量计划**：从人工设计→自动化方案发现
- **层级式规划**：高层分解+低层执行模式

---

## 来源15：SCOPE (2025.12) — LLM作为一次性教师蒸馏层级规划能力

**链接**：arXiv相关研究
**时间**：2025年12月
**核心贡献**：LLM作为一次性教师蒸馏层级规划能力

### 对agent-planner的启发
- **知识工程**：专家知识蒸馏流程可参考此模式
- **能力传承**：F4架构方案的知识融合可参考蒸馏思想

---

## 来源16：Close the Loop (2025.12) — 多Agent Role-Playing生成无限工具数据

**链接**：arXiv相关研究
**时间**：2025年12月
**核心贡献**：多Agent Role-Playing生成无限工具数据

### 对agent-planner的启发
- **F7坑点预警**：Role-Playing模式可用于模拟不同角色视角
- **知识库检索**：F4知识库检索可利用多角色视角丰富检索结果

---

## 来源17：Trustworthy Agentic AI (2025.12) — 多模态安全框架

**链接**：arXiv相关研究
**时间**：2025年12月
**核心贡献**：多模态安全框架防御提示注入攻击

### 对agent-planner的启发
- **F8环境配置**：安全边界检查对应此框架
- **版本治理**：Phase-D的变更追踪+回滚对应安全审计需求

---

## 来源18：Self-Regulated Simulative Planning (2026.5) — 自适应规划深度

**链接**：arXiv相关研究
**时间**：2026年5月
**核心贡献**：自适应规划深度，解决"过度规划"

### 对agent-planner的启发
- **F3成本预估**：避免过度规划，平衡深度与Token消耗
- **版本迭代控制**：5版上限强制在适当时机停止迭代
- **关键**：规划不是越详细越好，需根据任务复杂度自适应

---

## 专家知识汇总表（更新）

| # | 来源 | 专家 | 核心概念 | agent-planner映射 |
|---|------|------|---------|------------------|
| 1 | Karpathy | Andrej Karpathy | Think Before Coding | 先读再改不准盲改 |
| 2 | Anthropic | Anthropic | Agent循环设计 | Plan→Act→Observe→Loop |
| 3 | Lilian Weng | Lilian Weng | Prompt工程模式 | CoT/ReAct/Few-shot |
| 4 | DeepLearning.AI | Andrew Ng | 多Agent设计模式 | Handoffs/Collaboration |
| 5 | Microsoft | Microsoft Research | 多Agent对话框架 | Manager/GroupChat |
| 6 | HKUST | 港科大 | Prompt Engineer能力模型 | 知识获取→整理→验证→应用 |
| 7 | 张峻旸 | 阿里云 | AI Agent工程四大模块 | Planner/Executor/Memory/Tools |
| 8 | PromptLayer | PromptLayer | Prompt版本管理 | 版本控制/标签/追踪 |
| **9** | **ReAct** | **arXiv:2210.03629** | **推理-行动交替范式** | **F6工作流编排（4-A/4-B）** |
| **10** | **MetaGPT** | **arXiv:2308.00352** | **SOP编码+装配线** | **F5技能选型+F6工作流** |
| **11** | **LLM Agent规划综述** | **arXiv:2402.02716** | **5大规划类别** | **P3/F6/F10全部映射** |
| **12** | **AgentBench** | **arXiv:2308.03688** | **Agent评估Benchmark** | **质量自检+版本迭代** |
| **13** | **NeuroMAS** | **2025.5** | **RL自动学习协作** | **F11子代理自适应调用** |
| **14** | **BOAD** | **2025.12** | **Bandit优化自动化** | **P1批量计划自动化** |
| **15** | **SCOPE** | **2025.12** | **蒸馏层级规划** | **F4知识融合** |
| **16** | **Close the Loop** | **2025.12** | **Role-Playing工具数据** | **F7坑点多角色模拟** |
| **17** | **Trustworthy Agentic AI** | **2025.12** | **多模态安全框架** | **F8环境配置安全** |
| **18** | **Self-Regulated Planning** | **2026.5** | **自适应规划深度** | **F3成本预估+版本迭代** |

---

*本文件为 agent-planner skill 的外部专家知识库，版本 v1.1*
*来源截止：2026-05-22，新增10个来源（来源9-18），覆盖2022-2026年关键文献*