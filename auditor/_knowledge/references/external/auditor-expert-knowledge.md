# Auditor 专家知识库

> 收集专家知识来源,用于指导 auditor skill 的设计、实现与优化
> 版本:v1.0 | 2026-05-22

---

## 目录

1. [Karpathy 神经网络训练最佳实践](#1-karpathy-神经网络训练最佳实践)
2. [Prompt Engineering Guide 提示工程指南](#2-prompt-engineering-guide-提示工程指南)
3. [OpenAI Agents SDK 设计原则](#3-openai-agents-sdk-设计原则)
4. [Anthropic Claude 系统提示设计](#4-anthropic-claude-系统提示设计)
5. [软件工程中的审计与合规实践](#5-软件工程中的审计与合规实践)
6. [知识管理最佳实践](#6-知识管理最佳实践)
7. [Skill 系统设计原则](#7-skill-系统设计原则)
8. [Agent 系统架构模式](#8-agent-系统架构模式)

---

## 1. Karpathy 神经网络训练最佳实践

**来源**:Andrej Karpathy - *A Recipe for Training Neural Networks* (2019)
**链接**:https://karpathy.github.io/2019/04/25/recipe/

### 核心原则

#### 原则1:成为数据的知己(Become one with the data)

> "The first step to training a neural net is to not touch any neural net code at all and instead begin by thoroughly inspecting your data."

**在 auditor 中的应用**:
- 执行任何系统诊断前,先读取系统状态文件(memory-config.md、rules.md、agents-config.md)
- 理解当前上下文后再开始审计流程

#### 原则2:神经网络训练是漏水的抽象(Leaky Abstraction)

> "Neural net training fails silently. When you break or misconfigure code you will often get some kind of an exception... your misconfigured neural net will throw exceptions only if you're lucky; Most of the time it will train but silently work a bit worse."

**在 auditor 中的应用**:
- 审计过程必须可视化每一步的结果,不能假设"没报错=没问题"
- 质量门(Q-Gate)设计防止静默失败

#### 原则3:从简单到复杂(Simple to Complex)

> "What we try to prevent very hard is the introduction of a lot of 'unverified' complexity at once, which is bound to introduce bugs/misconfigurations that will take forever to find (if ever)."

**在 auditor 中的应用**:
- Phase-S 执行框架从 S1→S5 逐层推进
- 每个 Phase 设置质量门,未通过不进入下一阶段

#### 原则4:慢速思考(Slow and Deliberate)

> "A 'fast and furious' approach to training neural networks does not work and only leads to suffering. The qualities that in my experience correlate most strongly to success in deep learning are patience and attention to detail."

**在 auditor 中的应用**:
- auditor 执行不能追求速度,要追求准确性
- 超时场景有清晰的恢复流程

---

## 2. Prompt Engineering Guide 提示工程指南

**来源**:DAIR.AI - *Prompt Engineering Guide*
**链接**:https://www.promptingguide.ai/

### 核心技巧(适用于 auditor 的)

| 技巧 | 描述 | 在 auditor 中的应用 |
|------|------|-------------------|
| Zero-shot Prompting | 无示例直接指令 | auditor 的触发词机制就是零样本触发 |
| Few-shot Prompting | 提供少量示例 | 质量门判断逻辑可提供示例 |
| Chain-of-Thought | 逐步推理 | S1→S5 的阶段性输出就是 CoT |
| Self-Consistency | 多路径推理一致性 | 多维度质量门交叉验证 |
| Generated Knowledge | 先生成知识再回答 | S5 进化引擎生成经验知识 |

### 提示词设计原则

1. **清晰性**:指令明确,不歧义
2. **具体性**:给出具体步骤和格式要求
3. **分解性**:复杂任务分解为子任务
4. **可验证性**:输出结果必须有验证标准

---

## 3. OpenAI Agents SDK 设计原则

**来源**:OpenAI - *Agents SDK Documentation*
**链接**:(基于 SDK 设计理念整理)

### 核心概念

#### Agent 生命周期

```
输入 → 解释 → 规划 → 执行 → 输出 → 验证
```

#### 工具调用原则

- **单一职责**:每个工具做一件事
- **幂等性**:工具调用可重复且结果一致
- **超时处理**:工具调用必须有超时机制
- **错误恢复**:失败后有清晰的降级路径

#### Human-in-the-loop

- 关键决策需要人工确认
- 自动执行前有预览/dry-run 模式

### 在 auditor 中的对应设计

| OpenAI 概念 | auditor 对应 |
|-------------|-------------|
| Agent | auditor skill |
| Tools | skill 内的脚本和组件 |
| Guardrails | Layer0 Q-Gate 质量门 |
| Loop Detection | S5 进化引擎的自我改进 |
| Handoff | 子 Agent 间的结果传递 |

---

## 4. Anthropic Claude 系统提示设计

**来源**:Anthropic - *Building Effective Agents* (基于公开文档整理)

### 系统提示最佳实践

#### 原则1:角色和约束显式化

```
You are [role] with [capabilities]. You must [hard constraints].
```

auditor SKILL.md 的设计即遵循此原则:
```yaml
name: auditor
description: "系统优化审计员 + 财务合规审计助手..."
```

#### 原则2:边界明确化

- 明确列出能力范围
- 明确列出边界/限制
- 明确触发条件(强制触发词)

#### 原则3:输出格式标准化

- 每个阶段有明确的输出格式
- 输出包含置信度/状态标记
- 错误输出包含诊断信息

#### 原则4:上下文窗口管理

- 长期记忆 → memory-config.md / daily notes
- 技能知识 → _knowledge/ 目录
- 会话状态 → session manager
- 上下文卫生 → Q0 质量门清理

---

## 5. 软件工程中的审计与合规实践

**来源**:综合软件工程与审计理论

### 审计框架(通用)

| 阶段 | 活动 | auditor 对应 |
|------|------|-------------|
| 规划 | 确定范围、目标、资源 | Phase-G 目标分类 |
| 信息收集 | 获取证据、文档审阅 | S1 信息收集 |
| 分析 | 评估控制、识别问题 | S2-S3 分析 |
| 报告 | 记录发现、提出建议 | S5 报告生成 |
| 跟踪 | 确认整改、验证效果 | Layer2 版本治理 |

### 合规性检查要点

1. **可追溯性**:每个变更有记录、可回滚
2. **可验证性**:变更效果可量化评估
3. **职责分离**:变更者≠审批者≠执行者
4. **变更审批**:重要变更有审批流程

### 在 auditor 中的体现

- Phase-D 版本治理:变更追踪+回滚
- S3.3 变更验证:可验证指标
- S5.9 进化引擎:经验沉淀与复用
- 财务合规层L:内部控制与合规检查

---

## 6. 知识管理最佳实践

**来源**:知识工程领域研究

### 知识分层模型

| 层级 | 内容 | 加载方式 |
|------|------|---------|
| L1 热数据 | 首次加载必须的数据 | SKILL.md 加载时立即读取 |
| L2 温数据 | 按增强层自动加载 | 解析 SKILL.md 后自动加载 |
| L3 冷数据 | 按需触发词加载 | 命中触发词后按需注入 |
| L4 专家池 | 专家知识,按条件激活 | 版本治理或进化引擎触发 |

### 知识质量标准

1. **准确性**:知识内容正确无误
2. **完整性**:覆盖核心场景
3. **一致性**:与其他知识不冲突
4. **时效性**:定期更新
5. **可溯源**:标注知识来源

### auditor 的知识管理

```
_knowledge/
├── _components/      # L2 温数据(自动加载)
│   ├── context-hygiene.md
│   ├── behavior-checker.md
│   └── session-manager.md
├── _enhancement/     # L3 冷数据(按需加载)
│   ├── subagent-timeout-recovery.md
│   └── parallel-enhancement-batch.md
├── _index/           # 知识索引
├── _refined/         # L4 精选知识
├── references/       # 参考资料
├── core-principles/  # 核心原则(自学习沉淀)
└── scripts/         # 工具脚本
```

---

## 7. Skill 系统设计原则

**来源**:OpenClaw skill 设计规范(内部)

### Skill 黄金法则

1. **单一职责**:一个 skill 只做一个领域的事
2. **可被发现**:有清晰的触发词/描述
3. **可被发现**:有清晰的触发词/描述
4. **有生命周期**:创建→使用→优化→归档
5. **可被验证**:输出结果可验证

### Skill 接口设计

```yaml
# 标准 SKILL.md 结构
---
name: <skill-name>
description: "<触发词>|<用途>|<边界>"
---
# 内容
## 触发条件(何时使用)
## 执行流程(如何工作)
## 输出格式(什么结果)
## 依赖关系(需要什么)
```

### Skill 增强机制

| 增强类型 | 说明 | auditor 应用 |
|---------|------|-------------|
| A 增强 | CI/CD 集成 | skill-audit-suite |
| B 增强 | 行为规范化 | behavior-checker |
| C 增强 | Context 卫生 | context-hygiene |
| D 增强 | 子会话管理 | session-manager |
| E 增强 | 规划修正 | agent-planner |
| G 增强 | 自我进化 | self-improving |

---

## 8. Agent 系统架构模式

**来源**:Agent 系统研究综述

### 常见 Agent 架构

#### 反思架构(Reflexion)

```
执行 → 观察 → 反思 → 改进 → 执行
```

auditor 的 S5 进化引擎即基于此:
```python
if 同一类变更 >= 3次 出现缺陷记录:
    本地进化: self-improving → 更新技能自优化
    社区进化: >= 3次同类 → 上报 capability-evolver
```

#### Plan-Execute 架构

```
规划 → 执行 → 验证 → 反馈
```

auditor 的 P-Sub-P 规划修正即对应"规划"阶段。

#### Supervisor 架构

```
Supervisor → Sub-Agent 1
          → Sub-Agent 2
          → Sub-Agent 3
```

auditor 的 agent-team 增强层(H)即对应 Supervisor 模式。

### 多 Agent 协作模式

| 模式 | 说明 | auditor 应用 |
|------|------|-------------|
| Hierarchical | 层级管理 | 主agent→子agent |
| Collaborative | 协作完成 | agent-team 协作 |
| Competition | 竞态优化 | 多方案择优 |
| Debate | 辩论验证 | 多角度评审 |

---

## 9. NIST AI Risk Management Framework + GenAI Profile（2024-2026）— 官方AI风险管理框架

**来源**：NIST — *AI Risk Management Framework* + *Generative AI Profile (NIST-AI-600-1)*
**链接**：https://www.nist.gov/itl/ai-risk-management-framework | https://airc.nist.gov/airmf-resources/playbook/govern/
**时间**：GenAI Profile发布于2024年7月；关键基础设施AI RMF 2026年4月概念说明

### 核心原则（与auditor直接对应）

#### Govern函数首位
- **四大核心函数**：Govern（治理）> Map > Measure > Manage，治理是首位
- **auditor映射**：Phase-G目标分类即对应Govern函数

#### 变更管理政策强制规定
- 明确要求在AI风险管理政策中**详细规定变更管理需求**：版本控制、部署计划、监控计划
- **auditor映射**：Phase-S执行框架的S4.1变更验证即对应此要求

#### 模型文档清单系统
- 覆盖全生命周期：训练数据描述→算法方法论→测试验证→上线/变更计划
- **auditor映射**：Layer2版本治理的frozen_version.json即对应此清单

#### 风险分级制度
- 所有模型须分配风险等级，风险等级随生命周期动态变化
- **auditor映射**：S1.1的L1-L4风险分级和Phase-D版本治理

#### 审计轨迹（Audit Trail）
- 定期审查完整性、可用性、有效性
- **auditor映射**：S4.1的8项验证和S5.10经验报告格式

---

## 10. NIST AI RMF Playbook — Govern章节（2024）— AI治理实施指南

**来源**：NIST — *AI RMF Playbook Govern章节*
**链接**：https://airc.nist.gov/airmf-resources/playbook/govern/

### 核心观点

#### 风险量化公式
- **风险 ≈ 影响 × 可能性**，可用RAG（红黄绿）定性量表
- **auditor映射**：Phase-G的G3成功标准和S1.1的L1-L4风险等级

#### AI全链路文档要求
- AI参与者信息→业务理由→范围用途→风险→数据描述→算法→测试验证→依赖关系→部署监控→变更管理
- **auditor映射**：S1信息收集的8项准则和S5报告格式

#### 合规性审查
- AI系统须经过**适用法律/法规/标准合规性审查**，文档化监管环境
- **auditor映射**：增强层L财务合规的内部控制检查

---

## 11. GAO AI Accountability Framework（GAO-21-519SP，2021）— AI审计框架权威

**来源**：US Government Accountability Office
**链接**：https://www.gao.gov/products/gao-21-519sp
**时间**：2021年6月（被NIST AI RMF Playbook多次引用）

### 核心原则

#### 四大原则框架
- **Governance（治理）**、Data（数据）、Performance（性能）、Monitoring（监控）
- **auditor映射**：Phase-G + Phase-S + Phase-D的三阶段框架

#### 第三方审计重要性
- AI系统输入和操作**不总是可见** → 第三方评估和审计对实现负责任AI至关重要
- **auditor映射**：auditor作为独立第三方执行审查的必要性

#### 审计问题清单
- 为每个原则提供**审计问题清单和具体审计程序**
- **auditor映射**：Q0-Q6质量门检查项即对应此清单

---

## 12. AI Governance for Responsible ML Systems（arXiv:2211.13130，2022）— 学术治理框架

**来源**：NeurIPS 2022 TSRML Workshop
**链接**：https://arxiv.org/abs/2211.13130

### 核心观点

#### AI治理三重目标
1. **预防和缓解风险**
2. **从AI项目获取最大价值**
3. **建立组织级一致性**
- **auditor映射**：Phase-G目标分类对应第1条，Phase-S执行框架对应第3条

#### AI风险范围
- **监管/合规/声誉/用户信任/财务/社会风险**，概率性质导致风险远大于传统技术
- **auditor映射**：增强层L财务合规的各类风险检查

#### 透明度、可审计性、问责机制
- 须涵盖**设计/开发/部署/监控全阶段**
- **auditor映射**：Layer2版本治理的变更追踪+回滚能力

---

## 附录：专家知识索引（更新）

| 专家/来源 | 主题 | 关键贡献 |
|----------|------|---------|  
| Andrej Karpathy | 神经网络训练 | 漏水平板+从简到繁 |
| DAIR.AI | Prompt Engineering | CoT/Few-shot/Zero-shot |
| OpenAI | Agents SDK | 工具调用+生命周期 |
| Anthropic | Claude Agents | 角色+约束+格式 |
| 软件工程 | 审计框架 | 规划→执行→报告→跟踪 |
| 知识工程 | 知识分层 | L1-L4 热温冷专家池 |
| OpenClaw | Skill 设计 | 单一职责+可验证 |
| Agent 研究 | 架构模式 | Reflexion/Plan-Execute |
| **NIST AI RMF** | **AI风险管理** | **Govern函数首位+风险分级+审计轨迹** |
| **NIST AI RMF Playbook** | **AI治理实施** | **风险量化+全链路文档+合规审查** |
| **GAO AI Framework** | **AI审计框架** | **四大原则+第三方审计+审计清单** |
| **arXiv:2211.13130** | **ML治理学术** | **三重目标+风险范围+全阶段问责** |

**更新日志**：
- v1.1 (2026-05-22): 追加4个新来源（来源9-12），覆盖2024-2026年官方AI治理框架进展