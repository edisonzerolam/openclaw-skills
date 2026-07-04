#!/usr/bin/env python3
"""
子代理模板注入器 — 为 task(subagent_type=...) 的 prompt 注入方法论层。

在派发 subagent 时自动注入：
1. 复杂度判断 → System 1/2
2. 输出置信度标注要求
3. 预验尸检查（执行前）
4. 反馈循环指令

用法:
    # 注入到 task prompt
    python subagent_injector.py --task "分析茅台财报" --agent-type "researcher-ds"
    # 输出: 完整 injected prompt

    # 产出可复用的 prompt 模板
    python subagent_injector.py --task "写一个排序算法" --agent-type "fixer" --system "System 2"
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional


# ============================================================
# 方法论注入模板
# ============================================================

SYSTEM1_INJECTION = """
## 思维方法论（注入 — System 1 模式）

本任务已判定为 System 1（快速模式），请按以下规则执行：
1. 直接回答，无需多步推理
2. 如遇预期外的错误 → 停止自动重试，换一种方法
3. 输出附带置信度标注：
   - 确定性信息：无需标注
   - 推测性内容：标注「基于现有信息」
4. 如有多种可能解释，选最简单的那个（奥卡姆剃刀）
"""

SYSTEM2_INJECTION = """
## 思维方法论（注入 — System 2 模式）

本任务已判定为 System 2（深度推理模式），请按以下规则执行：

### 1. 第一性原理拆解
- 将任务拆解到不可再分的基础事实或基本约束
- 识别当前采用的假设，逐层追问「这个假设成立吗？」
- 从最底层的事实或约束出发向上构建方案

### 2. 预验尸检查（开始前）
- 花 10 秒想一下：如果这个任务会失败，最可能的原因是什么？
- 针对每个可能的风险，预设一个 fallback 链路

### 3. 输出置信度（完成后）
每个核心结论附带置信度：
- [高] > 0.9：直接陈述
- [中] 0.6-0.9：附带「基于现有信息推测」
- [低] < 0.6：标注「不确定」，说明需要什么额外信息

### 4. 反馈检查
- 如果中途遇到错误 → 分析根因（5Why 快速版），不是盲目重试
- 如果发现更好的方向 → 在验证后可以切换路径
"""  # noqa: W291


DEFAULT_OUTPUT_FORMAT = """
### 输出格式
请用结构化格式输出，包含：
1. 核心结论（附置信度）
2. 推理过程（可审计）
3. 使用的数据/来源（可追溯）
4. 如有不确定项 → 明确标注
"""


# ============================================================
# 注入器
# ============================================================

@dataclass
class InjectConfig:
    task: str
    agent_type: str = "general"
    system: str = "auto"  # auto, System 1, System 2
    output_format: bool = True
    extra_context: str = ""


class SubagentInjector:
    """为 subagent prompt 注入方法论层。"""

    def __init__(self, config: InjectConfig):
        self.config = config

    def inject(self) -> str:
        """生成注入方法论的完整 prompt。"""
        parts = []

        # 1. Task description
        parts.append(f"## 任务\n{self.config.task}")
        parts.append("")

        # 2. Methodology injection
        if self.config.system == "auto":
            # 自动判断：简单任务用 System 1，否则 System 2
            is_complex = self._judge_complexity(self.config.task)
            system = "System 2" if is_complex else "System 1"
            injection = SYSTEM2_INJECTION if is_complex else SYSTEM1_INJECTION
        elif self.config.system == "System 2":
            system = "System 2"
            injection = SYSTEM2_INJECTION
        else:
            system = "System 1"
            injection = SYSTEM1_INJECTION

        parts.append(f"## 思维模式：{system}")
        parts.append(injection.strip())
        parts.append("")

        # 3. Role-specific instructions
        if self.config.agent_type != "general":
            parts.append(f"## 角色\n你是 {self.config.agent_type} 专家。从专业角度完成任务。")
            parts.append("")

        # 4. Output format
        if self.config.output_format:
            parts.append(DEFAULT_OUTPUT_FORMAT.strip())
            parts.append("")

        # 5. Extra context
        if self.config.extra_context:
            parts.append(f"## 额外上下文\n{self.config.extra_context}")
            parts.append("")

        return "\n".join(parts)

    def _judge_complexity(self, task: str) -> bool:
        """
        快速判断任务是否复杂（System 2）。
        返回 True 表示需要深度推理。
        """
        task_lower = task.lower()

        # System 2 关键词
        complex_indicators = [
            "分析", "推理", "诊断", "评估", "比较", "对比",
            "规划", "设计", "架构", "方案", "策略",
            "重构", "迁移", "集成", "调试",
            "研究", "探索", "调查",
            "为什么", "原因", "影响", "后果",
        ]

        simple_indicators = [
            "查", "搜索", "查询", "翻译", "解释",
            "是什么", "今天", "现在", "多少",
        ]

        complex_score = sum(1 for w in complex_indicators if w in task_lower)
        simple_score = sum(1 for w in simple_indicators if w in task_lower)

        return complex_score > simple_score


# ============================================================
# 命令行入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="子代理模板注入器 — 为 subagent 注入方法论")
    parser.add_argument("--task", required=True, help="子代理任务描述")
    parser.add_argument("--agent-type", default="general", help="子代理类型 (researcher-ds, fixer, general 等)")
    parser.add_argument("--system", default="auto", choices=["auto", "System 1", "System 2"],
                        help="System 类型 (auto=自动判断)")
    parser.add_argument("--no-format", action="store_true", help="不添加默认输出格式")
    parser.add_argument("--context", help="额外上下文")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    config = InjectConfig(
        task=args.task,
        agent_type=args.agent_type,
        system=args.system,
        output_format=not args.no_format,
        extra_context=args.context or "",
    )

    injector = SubagentInjector(config)
    prompt = injector.inject()

    if args.json:
        result = {
            "task": args.task,
            "system": config.system if config.system != "auto" else injector._judge_complexity(args.task),
            "prompt": prompt,
            "length": len(prompt),
        }
        if config.system == "auto":
            result["judged_system"] = "System 2" if injector._judge_complexity(args.task) else "System 1"
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(prompt)


if __name__ == "__main__":
    main()
