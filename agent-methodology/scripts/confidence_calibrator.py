#!/usr/bin/env python3
"""
置信度校准器 — 对推理结论做贝叶斯置信度评分。

用法:
    # 单个结论评分
    python confidence_calibrator.py --claim "茅台2025年营收增长15%" --sources "季报原文" "财经分析"

    # 批量评分（JSON 输入）
    python confidence_calibrator.py --input ./conclusions.json

    # 交互式
    python confidence_calibrator.py --interactive

输入格式 (JSON):
    {
        "conclusions": [
            {
                "claim": "断言文本",
                "source_type": "官方文档|一手数据|媒体报道|推测",
                "evidence_strength": 0.0-1.0,
                "verifiable": true|false
            }
        ]
    }

输出:
    带置信度分数的结论列表
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional


# 来源类型 → 基础置信度
SOURCE_BASE_CONFIDENCE = {
    "官方文档": 0.85,
    "一手数据": 0.80,
    "原始文件": 0.90,
    "政府公告": 0.90,
    "学术论文": 0.75,
    "知名媒体报道": 0.55,
    "自媒体报道": 0.30,
    "个人观点": 0.15,
    "推测": 0.10,
    "用户输入": 0.60,
    "模型生成": 0.40,
}

# 证据强度调整
EVIDENCE_ADJUSTMENTS = {
    "high": +0.15,
    "medium": 0.0,
    "low": -0.15,
}


@dataclass
class Conclusion:
    claim: str
    source_type: str = "推测"
    evidence_strength: str = "medium"
    verifiable: bool = False
    confidence: float = 0.0
    label: str = ""
    note: str = ""


def calibrate(conclusion: Conclusion) -> Conclusion:
    """对单个结论做置信度校准。"""
    # 1. 基础置信度
    base = SOURCE_BASE_CONFIDENCE.get(conclusion.source_type, 0.20)

    # 2. 证据强度调整
    adj = EVIDENCE_ADJUSTMENTS.get(conclusion.evidence_strength, 0.0)
    base += adj

    # 3. 可验证奖励
    if conclusion.verifiable:
        base += 0.05

    # 4. 截断到 [0.05, 0.95]
    base = max(0.05, min(0.95, base))

    conclusion.confidence = round(base, 2)

    # 5. 标签
    if conclusion.confidence > 0.9:
        conclusion.label = "高置信度"
    elif conclusion.confidence >= 0.6:
        conclusion.label = "中等置信度"
    else:
        conclusion.label = "低置信度"

    return conclusion


def interactive_mode():
    """交互式置信度评估。"""
    print("=== 置信度校准器（交互模式）===")
    print("输入 'q' 退出\n")

    while True:
        claim = input("断言: ").strip()
        if claim.lower() in ("q", "quit", "exit"):
            break
        if not claim:
            continue

        print("\n来源类型:")
        for i, st in enumerate(SOURCE_BASE_CONFIDENCE.keys(), 1):
            print(f"  {i}. {st} ({SOURCE_BASE_CONFIDENCE[st]:.0%})")
        try:
            src_idx = int(input("选择来源类型 (编号): ")) - 1
            source_type = list(SOURCE_BASE_CONFIDENCE.keys())[src_idx]
        except (ValueError, IndexError):
            source_type = "推测"

        print("\n证据强度: 1=高 2=中 3=低")
        strength_map = {"1": "high", "2": "medium", "3": "low"}
        evidence_strength = strength_map.get(input("选择 (1-3): ").strip(), "medium")

        verifiable = input("可验证? (y/n): ").strip().lower() == "y"

        c = Conclusion(
            claim=claim,
            source_type=source_type,
            evidence_strength=evidence_strength,
            verifiable=verifiable,
        )
        result = calibrate(c)

        print(f"\n结果: [{result.label}] {result.confidence:.0%}")
        print(f"来源: {result.source_type}")
        print(f"证据: {result.evidence_strength}")
        print()


def batch_mode(input_path: str):
    """批量模式：从 JSON 文件读取结论列表。"""
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ 读取失败: {e}", file=sys.stderr)
        sys.exit(1)

    conclusions_data = data.get("conclusions", data if isinstance(data, list) else [])
    if isinstance(conclusions_data, dict):
        conclusions_data = [conclusions_data]

    results = []
    for item in conclusions_data:
        c = Conclusion(
            claim=item.get("claim", item.get("text", "")),
            source_type=item.get("source_type", "推测"),
            evidence_strength=item.get("evidence_strength", "medium"),
            verifiable=item.get("verifiable", False),
        )
        results.append(asdict(calibrate(c)))

    output = {
        "conclusions": results,
        "summary": {
            "total": len(results),
            "high_confidence": sum(1 for r in results if r["confidence"] > 0.9),
            "medium_confidence": sum(1 for r in results if 0.6 <= r["confidence"] <= 0.9),
            "low_confidence": sum(1 for r in results if r["confidence"] < 0.6),
        },
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


def single_mode(claim: str, sources: List[str]):
    """单条结论评估模式。"""
    # 从来源提示词推断来源类型
    source_text = " ".join(sources).lower()
    if any(w in source_text for w in ["官方", "政府", "公告", "原文件"]):
        source_type = "官方文档"
    elif any(w in source_text for w in ["一手", "原始", "数据来源", "直接"]):
        source_type = "一手数据"
    elif any(w in source_text for w in ["学术", "论文", "研究", "期刊"]):
        source_type = "学术论文"
    elif any(w in source_text for w in ["媒体", "报道", "新闻", "转载"]):
        source_type = "知名媒体报道"
    elif any(w in source_text for w in ["推测", "可能", "估计", "大概"]):
        source_type = "推测"
    else:
        source_type = "用户输入"

    c = Conclusion(
        claim=claim,
        source_type=source_type,
        evidence_strength="high" if len(sources) >= 2 else "medium",
        verifiable=True,
    )
    result = calibrate(c)
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="置信度校准器 — 贝叶斯信念更新")
    parser.add_argument("--claim", help="单条断言文本")
    parser.add_argument("--sources", nargs="*", default=[], help="来源描述")
    parser.add_argument("--input", help="批量模式：JSON 文件路径")
    parser.add_argument("--interactive", action="store_true", help="交互模式")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.input:
        batch_mode(args.input)
    elif args.claim:
        single_mode(args.claim, args.sources or [])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
