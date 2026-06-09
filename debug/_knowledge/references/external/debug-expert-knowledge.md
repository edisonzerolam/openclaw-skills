# debug 专家知识库

> 收集5-8个来源的专家知识，涵盖知识管理/技能设计/Prompt工程/Agent系统设计方向。

---

## 来源1：Karpathy — "Think Before Coding" 原则

**出处**：[Andrej Karpathy 博客/演讲](https://karpathy.github.io/)  
**核心思想**：在调试之前先理解问题结构，不要盲目试错。

### 关键原则

#### Think Before Coding
- **定义**：收到调试请求时，先用自然语言描述"预期行为 vs 实际行为"，再开始分析代码
- **适用场景**：任何 stacktrace/错误/崩溃分析
- **步骤**：
  1. 用户期望什么？
  2. 实际发生了什么？
  3. 差距在哪里？
  4. 最小化复现路径是什么？

#### 二进制思维
- 调试时将问题域一分为二：可能是A问题 / 不可能是A问题
- 每次诊断排除一半可能性（类似二分查找）

#### 最小化测试用例
- 将错误压缩到最小可复现单位再去分析
- 不要一次性看完整日志，先找关键时间窗口

---

## 来源2：DAIR.AI Prompt Engineering Guide

**出处**：[dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide)，[promptingguide.ai](https://www.promptingguide.ai/zh)  
**核心思想**：系统化提示词设计方法论

### 关键原则

#### Chain-of-Thought (CoT) 提示
- **定义**：通过分步推理引导LLM展示推理路径
- **适用场景**：复杂错误诊断、因果链分析
- **格式**：
  ```
  问题：日志显示 X 错误
  步骤1：分析 X 出现的位置
  步骤2：检查该位置的输入来源
  结论：原因是...
  ```

#### Few-Shot Prompting（少样本提示）
- 提供3-5个典型错误案例作为模式匹配参考
- **适用场景**：常见错误模式识别（OOM/Segfault/Timeout）
- **关键**：案例要覆盖"正确"和"错误"两种输出

#### ReAct（推理+行动）
- 结合推理步骤和工具调用
- **适用场景**：debug时需要运行命令验证假设

#### 提示词结构化要素
- 角色定义（Role）：你是一个专业debug助手
- 任务描述（Task）：分析以下日志，识别错误模式
- 输出格式（Format）：先列出假设，再逐一验证
- 约束条件（Constraint）：不要猜测，只基于日志内容

---

## 来源3：CAMEL 多智能体协作框架

**出处**：[CAMEL: Communicative Agents for "Mind" Exploration, arXiv:2303.17760](https://arxiv.org/abs/2303.17760)  
**核心思想**：通过 inception prompting 引导多个agent协作完成复杂任务

### 关键设计

#### Role-Playing Agent 架构
- **定义**：每个agent有明确角色（如"错误分析专家"、"日志追踪专家"）
- **优势**：分工明确，减少重复分析
- **适用场景**：复杂debug需要多维度分析时

#### Inception Prompting
- 在任务初始阶段明确所有agent的职责边界
- **示例**：
  ```
  你是一个日志分析专家，负责识别时间戳异常和错误聚集。
  不要跳到结论，先标记可疑点。
  ```

#### 自主协作协议
- 避免人类直接干预，agent之间通过消息传递协调
- **适用场景**：批量debug任务（如多个日志文件同时分析）

---

## 来源4：AgentBench — LLM作为Agent的评估体系

**出处**：[AgentBench: Evaluating LLMs as Agents, arXiv:2308.03688](https://arxiv.org/ abs/2308.03688)  
**核心思想**：评估LLM作为agent在真实环境中的决策能力

### 失败模式分类

AgentBench识别了LLM作为agent的主要失败原因：

1. **Long-term reasoning 不足** — 调试多步骤问题时容易丢失上下文
2. **Decision-making 缺陷** — 无法有效选择下一步诊断方向
3. **Instruction following 偏差** — 未严格遵循debug协议

### 适用建议

- debug时保持**上下文窗口简洁**，避免超长日志淹没关键信息
- 使用**分步验证**而非一步到位，每步都有明确结论
- 保持**指令一致性**：按照SKILL.md定义的流程执行

---

## 来源5：BytesAgain AI Skills — debug skill 源码

**出处**：[bytesagain/ai-skills](https://github.com/bytesagain/ai-skills)，debug skill  
**核心思想**：模块化脚本化debug工具设计

### 设计哲学

#### 分层知识架构（L1-L4）
| 层级 | 触发条件 | 内容 |
|------|---------|------|
| L1 | 首次加载 | SKILL.md 核心（6命令） |
| L2 | 诊断/错误/修复触发 | 健康检查+错误模式库 |
| L3 | 调试/验证/脚本触发 | Python验证脚本 |
| L4 | --expert 或复杂关键词 | 专家知识池 |

#### 命令解耦
- 每个命令独立：`trace`/`stacktrace`/`leaks`/`profile`/`diff-logs`/`http`
- 输入可以是文件路径或stdin（`-`）
- 输出格式统一：`error count + pattern summary + timestamps`

#### 并行执行 `[[PARALLEL]]`
- 多进程同时监控（leaks）
- 多命令同时度量（profile）
- 多端点同时探测（http）
- 多模式并行扫描（trace）

---

## 来源6：上下文工程（Context Engineering）

**出处**：[dair-ai/Prompt-Engineering-Guide - Context Engineering](https://github.com/dair-ai/Prompt-Engineering-Guide)  
**核心思想**：在AI Agent时代，上下文管理是核心技能

### 关键概念

#### 上下文窗口管理
- **核心问题**：上下文长度 vs 信息密度的权衡
- **debug场景应用**：不要把整个日志扔进去，先做预处理（grep/filter）

#### 知识检索增强（RAG）模式
- 将历史debug案例存入知识库
- 遇到新问题时先检索相似案例
- **适用场景**：重复错误模式识别

#### 上下文压缩策略
- 树形摘要：每层保留关键信息
- **debug应用**：从日志→错误摘要→根因分析→修复建议

---

## 来源7：结构化日志分析原则

**出处**：[OpenClaw rules.md + 通用日志工程最佳实践](https://promptguide.ai)  
**核心思想**：日志是debug的第一信息来源，需要结构化处理

### 结构化日志要素

```
[TIMESTAMP] [LEVEL] [SOURCE] [MESSAGE] [METADATA]
2024-01-01 10:00:00 ERROR app.py:42 Connection timeout {"host": "db", "timeout": 30}
```

### 分析优先级
1. **时间戳对齐** — 找到第一个错误发生的时间点
2. **错误级别过滤** — ERROR > WARN > INFO
3. **来源聚合** — 同一模块的错误归类
4. **模式识别** — 重复出现的错误归类

---

## 来源8：最小化干预原则

**出处**：综合 Karpathy + DevOps 最佳实践  
**核心思想**：debug时改动越少，验证越快，副作用越小

### 具体做法

1. **先读日志，再跑命令** — 不要还没看日志就开始重启服务
2. **最小化复现路径** — 找到触发bug的最简条件
3. **隔离变量** — 逐一排查，不要同时改多个参数
4. **回滚准备** — 每次修改前知道怎么恢复
5. **验证后才提交** — 修改后先在小范围验证再推广

---

---

## 来源9：Pydantic AI + Logfire（2024）— OpenTelemetry原生调试集成

**链接**：https://pydantic.dev/docs/ai/overview/ | https://pydantic.dev/docs/logfire/get-started/
**核心思想**：原生OpenTelemetry集成，`instrument_pydantic_ai()` 一行代码自动埋点，追踪Agent "反思-重试-纠正"过程

### 关键特性

#### 追踪Agent自纠正过程
- 对调试**幻觉/错误**特别有价值
- 可观测Agent的推理-行动-反馈循环
- 结构化输出 + 结构化日志一体化

#### 与debug skill的关联
- **适用场景**：复杂Agent调试需要追踪多跳推理链时
- **嵌入方式**：可在debug的`trace`命令中调用Logfire API记录中间状态
- **优势**：低侵入性，无需修改业务代码即可埋点

---

## 来源10：OpenTelemetry官方规范（2024）— AI/LLM语义标准

**链接**：https://opentelemetry.io/docs/specs/otel/
**核心思想**：行业标准，Traces/Metrics/Logs统一API，AI/LLM语义约定正在制定中

### 关键概念

#### Context传播机制
- **对debug的价值**：多跳Agent链路追踪，每个hop的上下文可传播
- **适用场景**：分布式Agent系统调试，需要关联多个子Agent的调用链

#### AI/LLM语义约定
- span属性标准化：model_name, token_count, temperature等
- **debug应用**：profile命令可输出符合OTel标准的trace

---

## 来源11：LiteLLM Callback观测（2024）— 统一错误映射

**链接**：https://docs.litellm.ai/docs
**核心思想**：`litellm.success_callback = ["langfuse", "mlflow", "helicone"]` 一行接入多个观测平台

### 关键特性

#### 统一错误映射
```python
AuthenticationError  # 401
RateLimitError       # 429
ContextLengthError   # 输入超限
```

- **debug价值**：debug skill的`http`命令可利用统一错误码快速分类
- **适用场景**：API调用调试，跨多个LLM提供商

#### MCP工具调用追踪
- 支持A2A Agent Gateway + MCP协议
- **debug应用**：`leaks`命令可监控MCP调用的资源消耗

---

## 来源12：LlamaIndex可观测性（2024）— 工作流事件驱动架构

**链接**：https://docs.llamaindex.ai/en/stable/
**核心思想**：内置评估/监控集成，Workflows事件驱动架构原生支持错误恢复日志

### 关键特性

#### reflection和error-correction模式追踪
- 内置对Agent自反思过程的可观测性支持
- **debug价值**：填补了"Agent自纠正过程可见性"这一当前最大空白

#### 工作流事件驱动
- 每个节点可埋点记录输入/输出/耗时
- **debug应用**：用于调试复杂工作流中的状态流转问题

---

## 专家知识整合摘要（更新）

| 来源 | 核心贡献 | 适用场景 |
|------|---------|---------|
| Karpathy | Think Before Coding，二分诊断 | 任何debug任务 |
| DAIR.AI PE Guide | CoT/Few-Shot/ReAct提示技术 | 复杂诊断推理 |
| CAMEL | 多Agent角色协作 | 批量/多维度debug |
| AgentBench | LLM失败模式分析 | 避免debug盲区 |
| BytesAgain | 分层知识+并行执行 | skill系统设计 |
| Context Engineering | 上下文管理+RAG | 长日志处理 |
| 结构化日志 | 时间戳+级别+来源 | 日志分析标准化 |
| 最小化干预 | 最小改动原则 | 修复策略 |
| **Pydantic AI+Logfire** | **OpenTelemetry原生集成，Agent自纠正追踪** | **复杂Agent调试** |
| **OpenTelemetry** | **AI/LLM语义标准，Context传播** | **分布式Agent链路追踪** |
| **LiteLLM Callback** | **统一错误映射，MCP追踪** | **API调用调试** |
| **LlamaIndex** | **reflection/error-correction追踪** | **工作流状态调试** |

**更新日志**：
- v1.1 (2026-05-22): 追加4个新来源（来源9-12），覆盖2024年可观测性最新进展