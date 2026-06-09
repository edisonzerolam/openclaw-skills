#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template

Usage:
    init_skill.py <skill-name> --path <path>

IMPORTANT: Always use the user-managed skills directory (~/.qclaw/skills) as the path.
Never create skills in the application's bundled skills directory (resources/openclaw/config/skills),
as that directory is replaced during application updates and user-created skills will be lost.

Examples:
    init_skill.py my-new-skill --path ~/.qclaw/skills
    init_skill.py my-api-helper --path ~/.qclaw/skills
"""

import sys
from pathlib import Path


TEMPLATES = {
    'tool': """---
name: {skill_name}
description: >
  [TODO: 触发场景] [关键动词] [目标对象].
  Use when [场景说明].
  NOT for: [反例1], [反例2], [反例3].
keywords: [kw1, kw2, kw3]
type: tool
---

# {skill_title}

## 📋 四原则质量门禁

| 原则 | 自检 | 说明 |
|------|------|------|
| ① 描述=路由器 | ❌ 待补充 | description 含触发场景+动词+反例边界 |
| ② 渐进式披露 | ❌ 待补充 | 本文件共 XX 行（≤200 ✓/✗） |
| ③ 从缺口出发 | ❌ 待补充 | 基于 ≥ 3 个真实任务失败观察 |
| ④ 代码兜底 | ❌ 待补充 | 确定性操作已标记 `run` 或 `read` |

> 任一 ❌ → 此 Skill 未达生产标准。详见 `references/anthropic-hardedge-template.md`

## 🎯 缺口声明

> **本文档解决了哪些具体的失败？**
>
> | # | 原始失败观察 | 解决方案 |
> |---|-------------|----------|
> | 1 | — （跑过 3-5 个真实任务后再填） | — |
> | 2 | — | — |
> | 3 | — | — |
>
> **不在 scope 内的场景：**
> - [场景 A] → 应该用 [other-skill-name] Skill
> - [场景 B] → 不在此 Skill 覆盖范围内

## 🛠️ 代码兜底清单

| 操作 | 方式 | 脚本/参考路径 |
|------|------|--------------|
| [确定性操作：排序/校验/格式转换] | `run` | `scripts/X.py` |
| [需要 LLM 判读的操作] | `read as reference` | `references/Y.md` |

## ℹ️ 三层加载结构

| 层级 | 内容 | 加载时机 | 红线 |
|------|------|----------|------|
| L1 路由层 | YAML frontmatter (name + description) | Agent 启动全量常驻 | ≤ 300 tokens |
| L2 主说明层 | 本文档正文（你正在读的内容） | Skill 触发后整体加载 | **≤ 200 行** |
| L3 资源层 | `references/` / `scripts/` / `assets/` | 按需点开阅读或执行 | 无上限 |

## Overview

[TODO: 1-2 句话说明此 Skill 提供的工具或功能。]

**典型用户请求：**
- "请帮我 [核心操作 1]"
- "我想 [核心操作 2]"

## Quick Start

### [核心操作 1]

```bash
python scripts/[script].py --input [path] --output [path]
```

### [核心操作 2]

```bash
python scripts/[script].py [参数]
```

> 💡 常用操作放在 Quick Start；复杂流程放在下方 Workflow 节（限 tool 型技能）

## Resources

| 路径 | 类型 | 说明 |
|------|------|------|
| `scripts/` | run | 工具脚本，直接执行 |
| `references/` | read | 参数说明 / 格式文档 |
| `assets/` | copy | 模板/图片/字体等 |

## ✅ 质量门禁自检清单

- [ ] description 含三要素（触发场景 + 关键动词 + 反例边界）
- [ ] L2 正文 ≤ 200 行
- [ ] 确定性操作已抽为脚本，标注 `run` 或 `read`
- [ ] 脚本至少已运行一次验证
- [ ] 参考文件名自解释（不是 `detail.md` 而是 `forms.md`）
- [ ] 所有 L3 文件在正文中被显式引用
- [ ] 元指导/TODO 行已删除
""",

    'knowledge': """---
name: {skill_name}
description: >
  [TODO: 触发场景] [遵循/遵守] [标准/规范名称].
  Use when [场景说明].
  NOT for: [反例1], [反例2], [反例3].
keywords: [kw1, kw2, kw3]
type: knowledge
---

# {skill_title}

## 📋 四原则质量门禁

| 原则 | 自检 | 说明 |
|------|------|------|
| ① 描述=路由器 | ❌ 待补充 | description 含触发场景+动词+反例边界 |
| ② 渐进式披露 | ❌ 待补充 | 本文件共 XX 行（≤200 ✓/✗） |
| ③ 从缺口出发 | ❌ 待补充 | 基于 ≥ 3 个真实任务失败观察 |
| ④ 代码兜底 | ❌ 待补充 | 确定性操作已标记 `run` 或 `read` |

> 任一 ❌ → 此 Skill 未达生产标准。详见 `references/anthropic-hardedge-template.md`

## 🎯 缺口声明

> **本文档解决了哪些具体的失败？**
>
> | # | 原始失败观察 | 解决方案 |
> |---|-------------|----------|
> | 1 | — （跑过 3-5 个真实任务后再填） | — |
> | 2 | — | — |
> | 3 | — | — |
>
> **不在 scope 内的场景：**
> - [场景 A] → 应该用 [other-skill-name] Skill
> - [场景 B] → 不在此 Skill 覆盖范围内

## 🛠️ 代码兜底清单

| 操作 | 方式 | 脚本/参考路径 |
|------|------|--------------|
| [确定性能校验/检查] | `run` | `scripts/X.py` |
| [需要 LLM 判读的规范判断] | `read as reference` | `references/Y.md` |

## ℹ️ 三层加载结构

| 层级 | 内容 | 加载时机 | 红线 |
|------|------|----------|------|
| L1 路由层 | YAML frontmatter (name + description) | Agent 启动全量常驻 | ≤ 300 tokens |
| L2 主说明层 | 本文档正文（你正在读的内容） | Skill 触发后整体加载 | **≤ 200 行** |
| L3 资源层 | `references/` / `scripts/` / `assets/` | 按需点开阅读或执行 | 无上限 |

## Overview

[TODO: 1-2 句话说明此规范/标准适用于什么场景。]

**典型用户请求：**
- "请按 [此规范] 审核 [内容]"
- "帮我检查 [输出] 是否符合 [标准]"

## Core Guidelines

### [关键规则 1]

[规则说明 + 好/坏案例]

### [关键规则 2]

[规则说明 + 好/坏案例]

## Specifications

| 维度 | 要求 | 例外 |
|------|------|------|
| [维度 A] | [要求说明] | [例外条件] |
| [维度 B] | [要求说明] | [例外条件] |

## Resources

| 路径 | 类型 | 说明 |
|------|------|------|
| `references/` | read | 完整规范 / 示例文档 |
| `scripts/` | run | 校验/检查脚本 |
| `assets/` | copy | 模板文件 |

## ✅ 质量门禁自检清单

- [ ] description 含三要素（触发场景 + 关键动词 + 反例边界）
- [ ] L2 正文 ≤ 200 行
- [ ] 确定性操作已抽为脚本，标注 `run` 或 `read`
- [ ] 脚本至少已运行一次验证
- [ ] 参考文件名自解释
- [ ] 所有 L3 文件在正文中被显式引用
- [ ] 元指导/TODO 行已删除
""",

    'workflow': """---
name: {skill_name}
description: >
  [TODO: 触发场景] [执行/完成] [流程名称].
  Use when [场景说明].
  NOT for: [反例1], [反例2], [反例3].
keywords: [kw1, kw2, kw3]
type: workflow
---

# {skill_title}

## 📋 四原则质量门禁

| 原则 | 自检 | 说明 |
|------|------|------|
| ① 描述=路由器 | ❌ 待补充 | description 含触发场景+动词+反例边界 |
| ② 渐进式披露 | ❌ 待补充 | 本文件共 XX 行（≤200 ✓/✗） |
| ③ 从缺口出发 | ❌ 待补充 | 基于 ≥ 3 个真实任务失败观察 |
| ④ 代码兜底 | ❌ 待补充 | 确定性操作已标记 `run` 或 `read` |

> 任一 ❌ → 此 Skill 未达生产标准。详见 `references/anthropic-hardedge-template.md`

## 🎯 缺口声明

> **本文档解决了哪些具体的失败？**
>
> | # | 原始失败观察 | 解决方案 |
> |---|-------------|----------|
> | 1 | — （跑过 3-5 个真实任务后再填） | — |
> | 2 | — | — |
> | 3 | — | — |
>
> **不在 scope 内的场景：**
> - [场景 A] → 应该用 [other-skill-name] Skill
> - [场景 B] → 不在此 Skill 覆盖范围内

## 🛠️ 代码兜底清单

| 操作 | 方式 | 脚本/参考路径 |
|------|------|--------------|
| [可自动化的流程步骤] | `run` | `scripts/X.py` |
| [需要人工/LLM 判断的环节] | `read as reference` | `references/Y.md` |

## ℹ️ 三层加载结构

| 层级 | 内容 | 加载时机 | 红线 |
|------|------|----------|------|
| L1 路由层 | YAML frontmatter (name + description) | Agent 启动全量常驻 | ≤ 300 tokens |
| L2 主说明层 | 本文档正文（你正在读的内容） | Skill 触发后整体加载 | **≤ 200 行** |
| L3 资源层 | `references/` / `scripts/` / `assets/` | 按需点开阅读或执行 | 无上限 |

## Overview

[TODO: 1-2 句话说明此流程解决什么问题。]

**典型触发场景：**
- "帮我完成 [流程]"
- "我想走 [流程]"

## Workflow Decision Tree

```mermaid
flowchart TD
  A[开始: [触发条件]] --> B{{决策点}}
  B -->|条件1| C[步骤1]
  B -->|条件2| D[步骤2]
```

## Step 1: [步骤名]

[操作说明 + 脚本/工具链接]

## Step 2: [步骤名]

[操作说明 + 脚本/工具链接]

## Step N: [步骤名]

[操作说明 + 脚本/工具链接]

## Resources

| 路径 | 类型 | 说明 |
|------|------|------|
| `references/` | read | 流程图 / 权限说明 / 常见失败模式 |
| `scripts/` | run | 自动化脚本 |
| `assets/` | copy | 流程模板文件 |

## ✅ 质量门禁自检清单

- [ ] description 含三要素（触发场景 + 关键动词 + 反例边界）
- [ ] L2 正文 ≤ 200 行
- [ ] 确定性操作已抽为脚本，标注 `run` 或 `read`
- [ ] 脚本至少已运行一次验证
- [ ] 参考文件名自解释
- [ ] 所有 L3 文件在正文中被显式引用
- [ ] 元指导/TODO 行已删除
""",

    'hybrid': """---
name: {skill_name}
description: >
  [TODO: 触发场景] [关键动词] [目标对象].
  Use when [场景说明].
  NOT for: [反例1], [反例2], [反例3].
keywords: [kw1, kw2, kw3]
type: hybrid
---

# {skill_title}

## 📋 四原则质量门禁

| 原则 | 自检 | 说明 |
|------|------|------|
| ① 描述=路由器 | ❌ 待补充 | description 含触发场景+动词+反例边界 |
| ② 渐进式披露 | ❌ 待补充 | 本文件共 XX 行（≤200 ✓/✗） |
| ③ 从缺口出发 | ❌ 待补充 | 基于 ≥ 3 个真实任务失败观察 |
| ④ 代码兜底 | ❌ 待补充 | 确定性操作已标记 `run` 或 `read` |

> 任一 ❌ → 此 Skill 未达生产标准。详见 `references/anthropic-hardedge-template.md`

## 🎯 缺口声明

> **本文档解决了哪些具体的失败？**
>
> | # | 原始失败观察 | 解决方案 |
> |---|-------------|----------|
> | 1 | — （跑过 3-5 个真实任务后再填） | — |
> | 2 | — | — |
> | 3 | — | — |
>
> **不在 scope 内的场景：**
> - [场景 A] → 应该用 [other-skill-name] Skill
> - [场景 B] → 不在此 Skill 覆盖范围内

## 🛠️ 代码兜底清单

| 操作 | 方式 | 脚本/参考路径 |
|------|------|--------------|
| [确定性操作：排序/校验/格式转换] | `run` | `scripts/X.py` |
| [需要 LLM 判读的操作] | `read as reference` | `references/Y.md` |

## ℹ️ 三层加载结构

| 层级 | 内容 | 加载时机 | 红线 |
|------|------|----------|------|
| L1 路由层 | YAML frontmatter (name + description) | Agent 启动全量常驻 | ≤ 300 tokens |
| L2 主说明层 | 本文档正文（你正在读的内容） | Skill 触发后整体加载 | **≤ 200 行** |
| L3 资源层 | `references/` / `scripts/` / `assets/` | 按需点开阅读或执行 | 无上限 |

## Overview

[TODO: 1-2 句话说明此 Skill 解决什么问题。]

**典型用户请求：**
- "请帮我 [典型操作 1]"
- "我想 [典型操作 2]"

## Quick Start

### [核心操作 1]

```bash
python scripts/[script].py --input [path] --output [path]
```

### [核心操作 2]

```bash
python scripts/[script].py [参数]
```

## Core Guidelines

### [关键指南 1]

[操作说明 + 好/坏案例]

## Resources

| 路径 | 类型 | 说明 |
|------|------|------|
| `scripts/` | run | 可执行脚本 |
| `references/` | read | 参考文档 |
| `assets/` | copy | 输出模板/图片/字体等 |

## ✅ 质量门禁自检清单

- [ ] description 含三要素（触发场景 + 关键动词 + 反例边界）
- [ ] L2 正文 ≤ 200 行
- [ ] 确定性操作已抽为脚本，标注 `run` 或 `read`
- [ ] 脚本至少已运行一次验证
- [ ] 参考文件名自解释
- [ ] 所有 L3 文件在正文中被显式引用
- [ ] 元指导/TODO 行已删除
""",
}


def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case for display."""
    return ' '.join(word.capitalize() for word in skill_name.split('-'))


def init_skill(skill_name, path, skill_type='hybrid'):
    """
    Initialize a new skill directory with template SKILL.md.

    Args:
        skill_name: Name of the skill
        path: Path where the skill directory should be created
        skill_type: 'tool' | 'knowledge' | 'workflow' | 'hybrid' (default)

    Returns:
        Path to created skill directory, or None if error
    """
    # Validate skill type
    if skill_type not in TEMPLATES:
        print(f"❌ Error: Unknown skill type '{skill_type}'. Valid: {', '.join(TEMPLATES.keys())}")
        return None

    # Determine skill directory path
    skill_dir = Path(path).resolve() / skill_name

    # Check if directory already exists
    if skill_dir.exists():
        print(f"❌ Error: Skill directory already exists: {skill_dir}")
        return None

    # Create skill directory
    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"✅ Created skill directory: {skill_dir}")
    except Exception as e:
        print(f"❌ Error creating directory: {e}")
        return None

    # Create SKILL.md from template
    skill_title = title_case_skill_name(skill_name)
    skill_content = TEMPLATES[skill_type].format(
        skill_name=skill_name,
        skill_title=skill_title
    )

    skill_md_path = skill_dir / 'SKILL.md'
    try:
        skill_md_path.write_text(skill_content, encoding='utf-8')
        print("✅ Created SKILL.md")
    except Exception as e:
        print(f"❌ Error creating SKILL.md: {e}")
        return None

    # Create resource directories (empty — no boilerplate files)
    try:
        (skill_dir / 'scripts').mkdir(exist_ok=True)
        (skill_dir / 'references').mkdir(exist_ok=True)
        (skill_dir / 'assets').mkdir(exist_ok=True)

        # Copy hardedge reference template into new skill
        _self_dir = Path(__file__).resolve().parent.parent
        hardedge_src = _self_dir / 'references' / 'anthropic-hardedge-template.md'
        if hardedge_src.exists():
            hardedge_dst = skill_dir / 'references' / 'anthropic-hardedge-template.md'
            hardedge_dst.write_text(hardedge_src.read_text(encoding='utf-8'), encoding='utf-8')
            print("✅ Copied references/anthropic-hardedge-template.md")
        else:
            print("⚠️  [SKIP] anthropic-hardedge-template.md not found")

        print("✅ Created empty directories: scripts/ references/ assets/")
    except Exception as e:
        print(f"❌ Error creating resource directories: {e}")
        return None

    # Print next steps
    print(f"\n✅ Skill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md — 填写 description 三要素 + 缺口声明 + 代码兜底清单")
    print("2. 完成 L2 正文内容（≤200 行）")
    print("3. 核对末尾自检清单，确认 7 项全部通过")
    print("4. Run package_skill.py 打包校验")

    return skill_dir


def main():
    if len(sys.argv) < 4 or sys.argv[2] != '--path':
        print("Usage: init_skill.py <skill-name> --path <path> [--type tool|knowledge|workflow|hybrid]")
        print("\nSkill name requirements:")
        print("  - Kebab-case identifier (e.g., 'my-data-analyzer')")
        print("  - Lowercase letters, digits, and hyphens only")
        print("  - Max 64 characters")
        print("  - Must match directory name exactly")
        print("\nSkill type options:")
        print("  --type tool      - Tool/API skill (Quick Start + core operations)")
        print("  --type knowledge - Knowledge/Guidelines skill (Core Guidelines + Specifications)")
        print("  --type workflow  - Workflow/Process skill (Decision Tree + Steps)")
        print("  --type hybrid    - Mixed-type skill (default; combines Quick Start + Guidelines)")
        print("\nIMPORTANT: Always use ~/.qclaw/skills as the path.")
        print("  Never use the bundled skills directory (resources/openclaw/config/skills)")
        print("  as it is replaced during application updates.")
        print("\nExamples:")
        print("  init_skill.py my-pdf-tool --path ~/.qclaw/skills --type tool")
        print("  init_skill.py brand-style --path ~/.qclaw/skills --type knowledge")
        print("  init_skill.py approval-flow --path ~/.qclaw/skills --type workflow")
        print("  init_skill.py my-api-helper --path ~/.qclaw/skills")
        sys.exit(1)

    skill_name = sys.argv[1]
    path = sys.argv[3]

    # Parse --type argument
    skill_type = 'hybrid'
    if '--type' in sys.argv:
        idx = sys.argv.index('--type')
        if idx + 1 < len(sys.argv):
            skill_type = sys.argv[idx + 1]

    print(f"🚀 Initializing skill: {skill_name}")
    print(f"   Type: {skill_type}")
    print(f"   Location: {path}")
    print()

    result = init_skill(skill_name, path, skill_type=skill_type)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
