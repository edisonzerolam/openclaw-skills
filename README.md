# OpenClaw Skills

A curated collection of modular, self-contained AI agent skills for the
[OpenClaw](https://github.com) framework. Each skill extends an AI agent's
capabilities with specialized knowledge, workflows, and tool integrations.

> **Note: This repository is an index/aggregator.** Each skill is also
> published as an independent repository for focused use and lighter-weight
> cloning. Use the links below to access the dedicated repository for each
> skill.

Language: **English** (current) | [简体中文](README.zh-CN.md)

---

## Skills

| Skill | Description | Repo |
|-------|-------------|------|
| **agent-planner** | Task planning, fact verification, audit workflow, F0-F12 pipeline | [edisonzerolam/agent-planner](https://github.com/edisonzerolam/agent-planner) |
| **auditor** | Systematic code and compliance audit, Phase G + S1-S5 stages | [edisonzerolam/auditor](https://github.com/edisonzerolam/auditor) |
| **debug** | Log tracing, crash analysis, memory leak detection, HTTP debugging | [edisonzerolam/debug](https://github.com/edisonzerolam/debug) |
| **agent-team-orchestration** | Multi-agent team coordination, roles, handoffs, quality gates | [edisonzerolam/agent-team-orchestration](https://github.com/edisonzerolam/agent-team-orchestration) |
| **qclaw-skill-creator** | Toolkit for creating new OpenClaw skills (Anthropic 4 hard constraints) | [edisonzerolam/qclaw-skill-creator](https://github.com/edisonzerolam/qclaw-skill-creator) |

---

## Installation

### Option 1: Install individual skills (recommended)

Clone only the skills you need:

```bash
git clone https://github.com/edisonzerolam/agent-planner.git
git clone https://github.com/edisonzerolam/auditor.git
# ... etc
```

### Option 2: Install all skills at once

Clone this aggregator repository and copy the skill directories you want:

```bash
git clone https://github.com/edisonzerolam/openclaw-skills.git
cp -r openclaw-skills/agent-planner ~/.openclaw-skills/
cp -r openclaw-skills/auditor ~/.openclaw-skills/
# ... etc
```

### Option 3: Cherry-pick from this repository

Browse the [skill directories](#skills) below and copy individual ones.

---

## Repository Structure

This repository mirrors all 5 skills under their original directory names:

```
openclaw-skills/
  README.md                  -- you are here
  LICENSE                    -- MIT License (applies to all subdirs)
  agent-planner/             -- mirror of edisonzerolam/agent-planner
  auditor/                   -- mirror of edisonzerolam/auditor
  debug/                     -- mirror of edisonzerolam/debug
  agent-team-orchestration/  -- mirror of edisonzerolam/agent-team-orchestration
  qclaw-skill-creator/       -- mirror of edisonzerolam/qclaw-skill-creator
```

> **Note:** The skill subdirectories in this repository are **mirrors** of the
> dedicated repos above. For the latest version and issue tracking, please use
> the dedicated repositories. The mirrors here are kept for convenience and
> aggregate discovery.

---

## Design Principles

All skills in this collection follow the same design philosophy:

1. **Modular and self-contained** -- each skill is a drop-in package
2. **Progressive disclosure** -- `SKILL.md` is the entry point, references/scripts
   load on demand
3. **Anthropic 4 hard constraints** -- description is the router, references are
   layered, deterministic steps use scripts
4. **Knowledge base separation** -- `_knowledge/` holds the deep reference
   material, separated from the public-facing skill structure
5. **MIT licensed** -- free to use, modify, and distribute

---

## License

MIT -- see [LICENSE](LICENSE) for full text.

Copyright (c) 2026 Edison Zero Lam

---

## Contributing

Issues and improvements should be filed in the **dedicated repository** for the
relevant skill (see the table above). This aggregator repository is read-only
mirrors.

---

## Releases

Each skill follows its own versioning. Latest stable releases:

- [agent-planner v1.0.0](https://github.com/edisonzerolam/agent-planner/releases/tag/v1.0.0)
- [auditor v1.0.0](https://github.com/edisonzerolam/auditor/releases/tag/v1.0.0)
- [debug v1.0.0](https://github.com/edisonzerolam/debug/releases/tag/v1.0.0)
- [agent-team-orchestration v1.0.0](https://github.com/edisonzerolam/agent-team-orchestration/releases/tag/v1.0.0)
- [qclaw-skill-creator v1.0.0](https://github.com/edisonzerolam/qclaw-skill-creator/releases/tag/v1.0.0)

---

## Note to Chinese Users / 致中国用户

This project is created and published by a Chinese developer. All public
repositories ship with **English + Simplified Chinese** bilingual READMEs.
If you spot any translation issue, feel free to open an issue or PR in the
dedicated repository.

本项目由中国开发者创建和发布。所有公开仓库都提供**英文 + 简体中文**双语
README。如果你发现任何翻译问题，欢迎在对应独立仓库提 Issue 或 PR。
