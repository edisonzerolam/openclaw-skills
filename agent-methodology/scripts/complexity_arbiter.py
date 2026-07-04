#!/usr/bin/env python3
"""
复杂度仲裁器 — 判断任务级别，路由到 System 1（快速）或 System 2（深度）。

用法:
    python complexity_arbiter.py --task "用户任务描述"
    python complexity_arbiter.py --task "任务描述" --json

输出:
    {
        "level": "L1" | "L2" | "L3" | "L4",
        "system": "System 1" | "System 2",
        "reason": "判断理由",
        "confidence": 0.0-1.0
    }
"""

import argparse
import json
import re
import sys


# 关键词权重配置
SYSTEM2_KEYWORDS = {
    # 推理类
    "分析": 0.3, "推理": 0.4, "诊断": 0.35, "评估": 0.3,
    "比较": 0.25, "对比": 0.25, "为什么": 0.3, "原因": 0.3,
    "影响": 0.25, "后果": 0.3,
    # 规划类
    "规划": 0.4, "设计": 0.35, "架构": 0.4, "方案": 0.3,
    "策略": 0.35, "路线图": 0.4, "计划": 0.3,
    # 跨领域
    "重构": 0.35, "迁移": 0.35, "集成": 0.3, "调试": 0.25,
    # 不确定/探索
    "研究": 0.35, "探索": 0.35, "调查": 0.3, "分析": 0.3,
}

SYSTEM1_KEYWORDS = {
    "查": -0.3, "搜索": -0.25, "查询": -0.3,
    "翻译": -0.3, "解释": -0.2, "是什么": -0.3,
    "今天": -0.3, "现在": -0.3,
}


def estimate_complexity(task: str) -> dict:
    """评估任务复杂度，返回路由建议。"""
    task_lower = task.lower()
    words = re.findall(r'[\w]+', task_lower)
    word_count = len(words)
    char_count = len(task)

    # 1. 关键词打分
    score = 0.0
    for kw, weight in SYSTEM2_KEYWORDS.items():
        if kw in task_lower:
            score += weight

    for kw, weight in SYSTEM1_KEYWORDS.items():
        if kw in task_lower:
            score += weight

    # 2. 长度因子：长任务通常更复杂
    if char_count > 200:
        score += 0.15
    elif char_count > 100:
        score += 0.05

    # 3. 确定性因子
    has_uncertainty = any(w in task_lower for w in ["可能", "或许", "不太确定", "如果", "假设"])
    if has_uncertainty:
        score += 0.2

    # 4. 多步因子
    numbered_steps = len(re.findall(r'\d+[\.\、\)]', task))
    if numbered_steps > 2:
        score += 0.15 * min(numbered_steps / 5, 1.0)

    # 5. 判断级别
    if score < 0.0:
        level = "L1"
        system = "System 1"
    elif score < 0.3:
        level = "L2"
        system = "System 1"
    elif score < 0.55:
        level = "L3"
        system = "System 2"
    else:
        level = "L4"
        system = "System 2"

    # 6. 置信度
    confidence = min(abs(score) + 0.5, 0.95)
    confidence = max(confidence, 0.5)

    # 7. 构建原因
    reasons = []
    if score > 0.3:
        reasons.append(f"推理/规划关键词权重 {score:.2f}")
    if char_count > 200:
        reasons.append(f"任务描述较长（{char_count}字）")
    if has_uncertainty:
        reasons.append("包含不确定性表述")
    if numbered_steps > 2:
        reasons.append(f"包含 {numbered_steps} 个步骤")

    reason = "；".join(reasons) if reasons else "基于关键词和长度综合分析"

    return {
        "level": level,
        "system": system,
        "reason": reason,
        "confidence": round(confidence, 2),
        "raw_score": round(score, 3),
    }


def main():
    parser = argparse.ArgumentParser(description="任务复杂度仲裁器 — 路由到 System 1 / System 2")
    parser.add_argument("--task", required=True, help="用户任务描述")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    result = estimate_complexity(args.task)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"任务级别: {result['level']}")
        print(f"路由系统: {result['system']}")
        print(f"判断理由: {result['reason']}")
        print(f"置信度:   {result['confidence']:.0%}")
        print(f"原始分:   {result['raw_score']:.3f}")


if __name__ == "__main__":
    main()
