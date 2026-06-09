# Q0 Context 健康检测

> 版本：v1.0 | 状态：active（内置）
> 来源：auditor Layer0 Q0 强制检查
> 定位：审计开始前的 Context 卫生检查，过滤噪音，确保审计质量

---

## 核心定位

在 Phase-G exit 后、Q1 之前执行 Context 健康检查。确保审计输入的 Context 干净、无干扰。

---

## 检查维度

### 1. 会话长度检查

| 指标 | 阈值 | 行动 |
|------|------|------|
| 会话消息数 | > 50 | 建议压缩 |
| 累积 token 估计 | > 8000 | 建议压缩 |
| 最近 10 条消息中噪音比例 | > 30% | 过滤 |

**噪音定义**：心跳消息、简单确认（"ok"/"好的"/"PERIODIC_CHECK_OK"）、与审计任务无关的闲聊

### 2. 上下文相关性检查

- 高相关 → 继续审计
- 低相关 → 记录"上下文切换"到 audit-template.md
- 无关 → 重新聚焦审计目标

### 3. 内存状态检查

- memory-config.md 是否存在且最新
- 最近 48h 内是否有相关审计记录
- 当前 workspace 与审计目标是否匹配

---

## 执行流程

```
Phase-G 结束
    ↓
Q0 Context 健康检查
    ↓
    ├── 会话长度 > 50 → 提示压缩（不阻塞）
    ├── 噪音比例 > 30% → 过滤噪音消息
    ├── 上下文低相关 → 记录上下文切换
    └── 内存缺失 → 尝试读取 memory-config.md
    ↓
输出：{healthy: bool, issues: [], recommendations: []}
    ↓
Q1 Skill 依赖缺口检查
```

---

## 输出格式

```yaml
Q0 检查结果:
  healthy: true|false
  issues:
    - type: "session_length|noise_ratio|context_switch|memory_missing"
      severity: "info|warn|block"
      description: "..."
      action: "..."
  recommendations:
    - "建议压缩最近的N条消息"
    - "过滤噪音消息"
  context_snapshot:
    recent_messages: n
    estimated_tokens: n
    noise_ratio: "0.xx"
    workspace_match: true|false
```

---

## 内置执行（无外部依赖）

auditor SKILL.md 内置 Q0 检查逻辑，无需调用外部脚本。

判断结果直接注入 audit-template.md。