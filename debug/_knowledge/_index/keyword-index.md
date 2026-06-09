## 关键词索引

> 基于 `external/debug-expert-knowledge.md` 生成的关键词映射表
> 格式：关键词 → 来源文件 # 来源/专家

---

### D - 调试方法论

debug疑难杂症 → external/debug-expert-knowledge.md # Karpathy 二分诊断法
堆栈追踪 → external/debug-expert-knowledge.md # BytesAgain stacktrace命令
内存泄漏检测 → external/debug-expert-knowledge.md # BytesAgain leaks命令
性能分析 → external/debug-expert-knowledge.md # BytesAgain profile命令
日志差异对比 → external/debug-expert-knowledge.md # BytesAgain diff-logs命令
HTTP调试 → external/debug-expert-knowledge.md # BytesAgain http命令

---

### E - 错误处理

错误模式识别 → external/debug-expert-knowledge.md # DAIR.AI PE Guide + BytesAgain
OOM内存溢出 → external/debug-expert-knowledge.md # BytesAgain错误模式库
Segfault段错误 → external/debug-expert-knowledge.md # BytesAgain错误模式库
FATAL致命错误 → external/debug-expert-knowledge.md # BytesAgain错误模式库
Timeout超时 → external/debug-expert-knowledge.md # BytesAgain错误模式库
Connection timeout → external/debug-expert-knowledge.md # 结构化日志原则
长推理链断裂 → external/debug-expert-knowledge.md # AgentBench LLM失败模式

---

### L - 日志分析

日志追踪 → external/debug-expert-knowledge.md # Karpathy + 结构化日志
时间戳对齐 → external/debug-expert-knowledge.md # 结构化日志原则
错误级别过滤 → external/debug-expert-knowledge.md # 结构化日志原则 (ERROR/WARN/INFO)
来源聚合 → external/debug-expert-knowledge.md # 结构化日志原则
最小化日志复现 → external/debug-expert-knowledge.md # Karpathy 最小化测试用例
日志压缩 → external/debug-expert-knowledge.md # Context Engineering上下文压缩

---

### P - Prompt工程

Chain-of-Thought → external/debug-expert-knowledge.md # DAIR.AI PE Guide
Few-Shot Prompting → external/debug-expert-knowledge.md # DAIR.AI PE Guide
ReAct推理行动 → external/debug-expert-knowledge.md # DAIR.AI PE Guide
Inception Prompting → external/debug-expert-knowledge.md # CAMEL多Agent框架
上下文窗口管理 → external/debug-expert-knowledge.md # Context Engineering
RAG知识检索 → external/debug-expert-knowledge.md # Context Engineering

---

### A - Agent系统

Agent调试 → external/debug-expert-knowledge.md # AgentBench评估体系
多Agent协作 → external/debug-expert-knowledge.md # CAMEL Role-Playing架构
角色分工协作 → external/debug-expert-knowledge.md # CAMEL inception prompting
Long-term reasoning → external/debug-expert-knowledge.md # AgentBench失败模式
Decision-making缺陷 → external/debug-expert-knowledge.md # AgentBench失败模式
Instruction following偏差 → external/debug-expert-knowledge.md # AgentBench失败模式

---

### S - 技能设计

分层知识架构 → external/debug-expert-knowledge.md # BytesAgain L1-L4设计
并行执行 → external/debug-expert-knowledge.md # BytesAgain [[PARALLEL]]机制
命令解耦 → external/debug-expert-knowledge.md # BytesAgain模块化设计
知识库健康检查 → external/debug-expert-knowledge.md # BytesAgain knowledge-health机制
触发词匹配 → external/debug-expert-knowledge.md # BytesAgain L2/L3加载规则
专家知识池 → external/debug-expert-knowledge.md # BytesAgain L4按需加载

---

---

### N - 可观测性（新）

OpenTelemetry → external/debug-expert-knowledge.md # 来源10 AI/LLM语义标准
Otel Trace → external/debug-expert-knowledge.md # 来源10 Context传播机制
Pydantic AI调试 → external/debug-expert-knowledge.md # 来源9 Agent自纠正追踪
Logfire → external/debug-expert-knowledge.md # 来源9 OpenTelemetry原生集成
LiteLLM Callback → external/debug-expert-knowledge.md # 来源11 统一错误映射
LlamaIndex可观测 → external/debug-expert-knowledge.md # 来源12 reflection追踪
MCP工具追踪 → external/debug-expert-knowledge.md # 来源11 A2A Agent Gateway

---

### M - 方法原则

先诊后断 → external/debug-expert-knowledge.md # Karpathy Think Before Coding
最小化干预 → external/debug-expert-knowledge.md # DevOps最佳实践
二分查找诊断 → external/debug-expert-knowledge.md # Karpathy 二进制思维
隔离变量排查 → external/debug-expert-knowledge.md # 最小化干预原则
回滚准备 → external/debug-expert-knowledge.md # 最小化干预原则
验证后提交 → external/debug-expert-knowledge.md # 最小化干预原则