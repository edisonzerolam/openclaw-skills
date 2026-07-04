# OpenClaw Skills（中文版）

一个模块化、自包含的 AI 智能体技能集合，用于 [OpenClaw](https://github.com) 框架。
每个技能都用专门的知识、工作流和工具集成来扩展 AI 智能体的能力。

> **📢 本仓库是索引/聚合仓库。** 每个技能都同时发布为独立仓库，
> 方便聚焦使用和轻量级克隆。请使用下方链接访问各技能的独立仓库。

🌐 **语言**: [English](README.md) | **简体中文**（当前）

---

## 🚀 技能列表

| 技能 | 描述 | 独立仓库 |
|------|------|----------|
| **agent-planner** | 任务规划、事实验证、审计工作流、F0-F12 流程 | [edisonzerolam/agent-planner](https://github.com/edisonzerolam/agent-planner) |
| **auditor** | 系统化代码与合规审计，Phase G + S1-S5 阶段 | [edisonzerolam/auditor](https://github.com/edisonzerolam/auditor) |
| **debug** | 日志追踪、崩溃分析、内存泄漏检测、HTTP 调试 | [edisonzerolam/debug](https://github.com/edisonzerolam/debug) |
| **agent-team-orchestration** | 多 agent 团队协作、角色、交接、质量门禁 | [edisonzerolam/agent-team-orchestration](https://github.com/edisonzerolam/agent-team-orchestration) |
| **qclaw-skill-creator** | 创建新 OpenClaw 技能的工具包（Anthropic 4 条硬约束） | [edisonzerolam/qclaw-skill-creator](https://github.com/edisonzerolam/qclaw-skill-creator) |
| **agent-methodology** | P0 核心方法论技能 — 双系统分治、预验尸、贝叶斯置信度、反馈循环、谬误检测 | [edisonzerolam/openclaw-skills/tree/main/agent-methodology](https://github.com/edisonzerolam/openclaw-skills/tree/main/agent-methodology) |

---

## 📦 安装

### 方式 1：单独安装技能（推荐）

只克隆你需要的技能：

```bash
git clone https://github.com/edisonzerolam/agent-planner.git
git clone https://github.com/edisonzerolam/auditor.git
# ... 等等
```

### 方式 2：一次性安装全部技能

克隆本聚合仓库，再复制你想要的子目录：

```bash
git clone https://github.com/edisonzerolam/openclaw-skills.git
cp -r openclaw-skills/agent-planner ~/.openclaw-skills/
cp -r openclaw-skills/auditor ~/.openclaw-skills/
# ... 等等
```

### 方式 3：从本仓库挑选

浏览下方的[技能目录](#-技能目录)，按需复制单个子目录。

---

## 📂 仓库结构

本仓库以原始目录名镜像了全部 6 个技能：

```
openclaw-skills/
├── README.md                  ← 你在这里
├── README.zh-CN.md            ← 简体中文版
├── LICENSE                    ← MIT 许可证（适用于所有子目录）
├── agent-planner/             ← edisonzerolam/agent-planner 的镜像
├── auditor/                   ← edisonzerolam/auditor 的镜像
├── debug/                     ← edisonzerolam/debug 的镜像
├── agent-team-orchestration/  ← edisonzerolam/agent-team-orchestration 的镜像
├── qclaw-skill-creator/       ← edisonzerolam/qclaw-skill-creator 的镜像
└── agent-methodology/         ← P0 核心方法论（双系统分治、预验尸、贝叶斯置信度、谬误检测）
```

> **注意：** 本仓库中的技能子目录是上方独立仓库的**镜像**。
> 如需最新版本和问题跟踪，请使用对应的独立仓库。本仓库的镜像仅为方便聚合发现。

---

## 🎯 设计原则

本集合中的所有技能遵循相同的设计哲学：

1. **模块化和自包含** — 每个技能都是即插即用的包
2. **渐进式披露** — `SKILL.md` 是入口点，references/scripts 按需加载
3. **Anthropic 4 条硬约束** — 描述作为路由、references 分层、确定性步骤用脚本
4. **知识库分离** — `_knowledge/` 存放深度参考资料，与面向公众的技能结构分离
5. **MIT 许可证** — 可自由使用、修改、分发

---

## 📜 许可证

MIT — 完整文本见 [LICENSE](LICENSE)。

Copyright (c) 2026 Edison Zero Lam

---

## 🤝 贡献

问题和改进应在相关技能的**独立仓库**中提出（见上表）。本聚合仓库的镜像是只读的。

---

## 📌 版本

每个技能各自独立版本控制。最新稳定版：

- [agent-planner v1.0.0](https://github.com/edisonzerolam/agent-planner/releases/tag/v1.0.0)
- [auditor v1.0.0](https://github.com/edisonzerolam/auditor/releases/tag/v1.0.0)
- [debug v1.0.0](https://github.com/edisonzerolam/debug/releases/tag/v1.0.0)
- [agent-team-orchestration v1.0.0](https://github.com/edisonzerolam/agent-team-orchestration/releases/tag/v1.0.0)
- [qclaw-skill-creator v1.0.0](https://github.com/edisonzerolam/qclaw-skill-creator/releases/tag/v1.0.0)

---

## 🙋 致中国用户

本项目由一位中国开发者创建和发布，原始工作语言为中文。所有公开仓库都提供
**英文 + 简体中文**双语 README。如果你看到任何英文翻译不准确或中文表达有问题，
欢迎在对应独立仓库提 Issue 或 PR 协助改进。
