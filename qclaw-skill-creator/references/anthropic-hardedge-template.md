# Anthropic 四硬核工程原则 — Skill 模板参考

> 来源：《Equipping agents for the real world with Agent Skills》, Anthropic Engineering, 2025-10-16
> 嵌入自 qclaw-skill-creator

创建 Skill 时，**用这份清单逐条校验**。跳过任何一条都意味着这个 Skill 不达标。

---

## ① 描述 = 路由器（不是简介）

**不要写：**
```
description: A comprehensive skill for data analysis
```
→ 太宽泛，会和所有"分析"类任务抢触发，谁也干不好。

**要写：**
```
description: >
  Use when user asks to sort/filter/aggregate CSV or JSON data,
  especially multi-file batch operations.
  NOT for: SQL queries, pandas DataFrame manipulation, or chart rendering.
```

**自检：**
- [ ] description 含**三要素**：触发场景 + 关键动词 + 反例边界（什么情况不触发）
- [ ] name ≤ 64 字符，动词优先（`sort-data` > `data-sorting-tool`）
- [ ] 如果一个 Agent 安装了 10 个 Skill，description 能让它在 1 秒内选出对的

---

## ② 渐进式披露的三层加载

| 层级 | 内容 | 加载时机 | 容量红线 |
|------|------|----------|----------|
| L1 路由层 | YAML frontmatter (name + description) | Agent 启动时全量常驻 system prompt | ≤ 300 token |
| L2 主说明层 | SKILL.md 正文 | Skill 触发后加载 | ≤ 200 行 |
| L3 资源层 | `references/` / `scripts/` / `assets/` | 触发后按需点开 | 无上限 |

**自检：**
- [ ] L2 超过 200 行 → 已拆文件，没有硬塞
- [ ] **互斥场景**（"填表单"和"合并 PDF"同时不出现）→ **已拆到不同文件**，不在同一份 SKILL.md 里
- [ ] L3 文件名自解释（`forms.md` 而不是 `detail.md`，`scripts/rotate_pdf.py` 而不是 `utils.py`）
- [ ] 每个额外 .md 文件都在 SKILL.md 正文中被显式引用并说明何时读取
- [ ] 代码脚本同时是"工具"+"文档"：description / SKILL.md 里写清了 **该跑脚本** 还是 **该读文件内容**

---

## ③ 从缺口出发，不从蓝图出发

**原文：** "Start with evaluation: Identify specific gaps in your agents' capabilities by running them on representative tasks and observing where they struggle or require additional context. Then build skills incrementally to address these shortcomings."

**自检：**
- [ ] 跑过 3-5 个真实任务，记下了具体卡点
- [ ] 能回答："这个 Skill 修好了哪一类具体的失败？"
- [ ] Skill 的 scope 只覆盖这些失败，不往外扩
- [ ] 不拍脑袋建"项目管理大 Skill"——原文："Multiple focused skills compose better than one large skill."
- [ ] 如果有 2 个不相关的场景，分成 2 个 Skill

---

## ④ 确定性步骤必须用脚本兜底

**原文：** "Certain operations are better suited for traditional code execution... Many applications require the deterministic reliability that only code can provide."

这条没有商量余地。**以下工作不给 LLM 推理：**

| 必须脚本（确定性的）| 留给 LLM（需要判断的）|
|---------------------|---------------------|
| 排序 / 校验 / 正则匹配 | 判断 / 解释 / 规划 |
| 数值计算 / 格式转换 | 文案 / 润色 / 写文章 |
| 数据提取 / 结构化 | 错误定位 / 决策 |

**自检：**
- [ ] 每个脚本在 SKILL.md 里标注：**`run scripts/X.py`** 还是 **`read scripts/X.py as reference`**
- [ ] "靠 Prompt 做质量检查 = 不能上生产"——这条线画清楚了
- [ ] 凡是重复 2 次以上的操作，已抽成脚本

---

## 补充：原文容易被忽略的两条

**⑤ 安全审计**
- Skill 含可执行代码 ⇔ 信任边界
- 只装可信源
- 三方 Skill 装前审计所有文件和依赖

**⑥ 跨产品通用**
- 遵循 agentskills.io 开放标准
- 同一格式在 Claude.ai / Claude Code / API / Agent SDK 通用
- name ≤ 64 字符，YAML frontmatter 格式合规
