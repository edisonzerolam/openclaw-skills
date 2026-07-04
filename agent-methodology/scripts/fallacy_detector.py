#!/usr/bin/env python3
"""
谬误检测器 — 扫描文本中的逻辑谬误。

支持的谬误类型（8+种）:
1. 诉诸人身 (Ad Hominem)
2. 稻草人 (Straw Man)
3. 滑坡 (Slippery Slope)
4. 假因果 (Post Hoc Ergo Propter Hoc)
5. 虚假两难 (False Dilemma)
6. 诉诸权威 (Appeal to Authority)
7. 诉诸多数 (Bandwagon)
8. 循环论证 (Begging the Question)
9. 幸存者偏差 (Survivorship Bias)
10. 轶事证据 (Anecdotal Fallacy)

用法:
    # 直接扫描文本
    python fallacy_detector.py --text "因为大多数人都同意，所以这是对的"

    # 扫描文件
    python fallacy_detector.py --file ./output.md

    # JSON 输出
    python fallacy_detector.py --text "..." --json
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple


# ============================================================
# 谬误模式定义
# ============================================================

@dataclass
class FallacyPattern:
    name: str
    description: str
    patterns: List[str]  # 正则列表
    severity: str  # low, medium, high
    suggestion: str


FALLACY_PATTERNS = [
    FallacyPattern(
        name="虚假两难 (False Dilemma)",
        description="只给出两个极端选项，忽略中间地带和其他可能性",
        patterns=[
            r"(要么|不是|要不).{0,20}(要么|就是|便是).{0,20}(没有其他选择|别无选择|只有这两条路)",
            r"(只有两个选择|非此即彼|不是A就是B|要么对要么错)",
            r"(如果不.*就只能|不.*就必然)",
        ],
        severity="medium",
        suggestion="补充更多选项，检查是否存在中间地带或第三方案",
    ),
    FallacyPattern(
        name="诉诸多数 (Bandwagon)",
        description="仅因多数人认同或流行就认为正确",
        patterns=[
            r"(大多数人|大家|人人|所有人|群众|主流)都.{0,10}(认同|认为|同意|喜欢|支持|选择)",
            r"(流行|热门|大家都在用|趋势是).{0,20}(所以|因此|说明)",
            r"(千万人|亿万人|无数人).{0,10}(选择|使用|推荐)",
        ],
        severity="low",
        suggestion="补充实质性论据，流行度不等于正确性",
    ),
    FallacyPattern(
        name="诉诸权威 (Appeal to Authority)",
        description="仅凭权威身份（专家/名人/机构）断言正确，无实质论证",
        patterns=[
            r"(专家|教授|博士|院士|权威).{0,10}(说|指出|认为|表示|建议).{0,20}(所以|因此|说明|就是)",
            r"(据.{0,5}研究|研究表明|科学证明).{0,30}(所以|因此)",
            r"(诺贝尔奖|院士|教授).{0,20}(认为|表示)",
        ],
        severity="medium",
        suggestion="权威引用应附带具体论证和数据，而非仅依赖身份",
    ),
    FallacyPattern(
        name="滑坡谬误 (Slippery Slope)",
        description="断言一步将导致极端后果，缺乏中间环节论证",
        patterns=[
            r"(如果|一旦).{0,20}(就会|必将|必然导致).{0,20}(灾难|崩溃|毁灭|无法挽回|不可收拾)",
            r"放任.{0,15}(就会|必然).{0,15}(泛滥|失控|不可控)",
            r"(开了这个口子|迈出这一步).{0,20}(就再也|就无法|后果不堪)",
        ],
        severity="medium",
        suggestion="补充中间环节的因果论证，检查每个环节是否真的必然发生",
    ),
    FallacyPattern(
        name="假因果 (Post Hoc)",
        description="先后关系误认为因果关系（A在B之前发生，所以A导致B）",
        patterns=[
            r"(之后|随后|紧接着).{0,10}(就|便|于是).{0,30}(说明|证明|表明).{0,10}(导致|引起|因为)",
            r"(自从|自.*以来).{0,20}(就|便).{0,30}(所以|因此)",
        ],
        severity="high",
        suggestion="前后关系不等于因果关系，需排除其他变量，补充因果机制解释",
    ),
    FallacyPattern(
        name="循环论证 (Begging the Question)",
        description="结论暗含在前提中，论证循环",
        patterns=[
            r"因为.{0,30}(所以|因此).{0,30}(就是|本质是|其实就是).{0,10}\1",
            r"(显然|不言而喻|众所周知).{0,20}(所以|因此).{0,30}(这就是为什么)",
        ],
        severity="high",
        suggestion="检查前提中是否已经隐含了待证明的结论",
    ),
    FallacyPattern(
        name="幸存者偏差 (Survivorship Bias)",
        description="只关注成功者/幸存者，忽略失败者",
        patterns=[
            r"(成功.{0,5})(的企业|的人|的案例|的经历).{0,20}(都|都是|无一例外)",
            r"(那些.{0,10}成功.{0,10})(都|都是|证明).{0,20}(方法|模式|路径)",
            r"只看.{0,10}(成功|活下来|盈利).{0,20}(总结|分析)",
        ],
        severity="medium",
        suggestion="同时分析失败案例，确认成功因素在失败案例中是否也出现",
    ),
    FallacyPattern(
        name="轶事证据 (Anecdotal Fallacy)",
        description="用个别案例否定统计数据或普遍规律",
        patterns=[
            r"(我.{0,5}有个|我认识|我听说|我有一个).{0,20}(朋友|同事|亲戚|客户).{0,30}(所以|说明|证明)",
            r"(虽然数据|虽然统计|虽然概率).{0,30}(但是|然而).{0,20}(例子|案例|个例)",
            r"(就有.{0,5}个.{0,5}人|我就见过|真人真事).{0,30}(说明|证明|打脸)",
        ],
        severity="medium",
        suggestion="个别案例不能否定统计规律，区分个案与总体趋势",
    ),
    FallacyPattern(
        name="稻草人 (Straw Man)",
        description="歪曲/简化对方立场后再驳斥",
        patterns=[
            r"你的意思不就是.{0,30}(吗|吧|么)",
            r"按你的逻辑.{0,30}(岂不|那岂不是|那不就)",
            r"所以你觉得.{0,30}(反对|讨厌|不喜欢).{0,10}(一切|所有|全部)",
        ],
        severity="high",
        suggestion="先确认对方真实立场，避免过度简化或极端化",
    ),
]


# ============================================================
# 检测器
# ============================================================

class FallacyDetector:
    """逻辑谬误检测器。"""

    def __init__(self, patterns: Optional[List[FallacyPattern]] = None):
        self.patterns = patterns or FALLACY_PATTERNS
        self._compiled = [
            (p, re.compile("|".join(f"(?:{pt})" for pt in p.patterns), re.IGNORECASE))
            for p in self.patterns
        ]

    @dataclass
    class Match:
        fallacy: str
        description: str
        matched_text: str
        position: Tuple[int, int]
        severity: str
        suggestion: str
        context: str = ""

    def scan(self, text: str, context_chars: int = 30) -> List[Match]:
        """扫描文本中的所有谬误匹配。"""
        matches = []
        for pattern_def, compiled in self._compiled:
            for match in compiled.finditer(text):
                start, end = match.start(), match.end()
                matched_text = match.group()

                # 提取上下文
                ctx_start = max(0, start - context_chars)
                ctx_end = min(len(text), end + context_chars)
                context = text[ctx_start:ctx_end]

                matches.append(self.Match(
                    fallacy=pattern_def.name,
                    description=pattern_def.description,
                    matched_text=matched_text,
                    position=(start, end),
                    severity=pattern_def.severity,
                    suggestion=pattern_def.suggestion,
                    context=context,
                ))

        return matches

    def scan_file(self, filepath: str, encoding: str = "utf-8") -> List[Match]:
        """扫描文件。"""
        with open(filepath, "r", encoding=encoding) as f:
            text = f.read()
        return self.scan(text)

    def analyze(self, text: str) -> Dict:
        """返回分析报告。"""
        matches = self.scan(text)

        severity_order = {"high": 0, "medium": 1, "low": 2}
        matches.sort(key=lambda m: severity_order.get(m.severity, 99))

        # 按严重度统计
        by_severity = {"high": 0, "medium": 0, "low": 0}
        by_type = {}
        for m in matches:
            by_severity[m.severity] = by_severity.get(m.severity, 0) + 1
            by_type[m.fallacy] = by_type.get(m.fallacy, 0) + 1

        # 风险评级
        if by_severity.get("high", 0) >= 2:
            risk_level = "high"
        elif by_severity.get("high", 0) >= 1 or by_severity.get("medium", 0) >= 3:
            risk_level = "medium"
        elif matches:
            risk_level = "low"
        else:
            risk_level = "none"

        return {
            "total_matches": len(matches),
            "risk_level": risk_level,
            "by_severity": by_severity,
            "by_type": by_type,
            "matches": [
                {
                    "fallacy": m.fallacy,
                    "matched_text": m.matched_text,
                    "severity": m.severity,
                    "suggestion": m.suggestion,
                    "context": m.context,
                }
                for m in matches
            ],
        }


# ============================================================
# 命令行入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="谬误检测器 — 逻辑谬误扫描")
    parser.add_argument("--text", help="直接输入待扫描的文本")
    parser.add_argument("--file", help="扫描文件")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--list", action="store_true", help="列出支持的谬误类型")
    args = parser.parse_args()

    detector = FallacyDetector()

    if args.list:
        print("支持的谬误类型:\n")
        for p in FALLACY_PATTERNS:
            sev_icon = {"high": "🔴", "medium": "🟡", "low": "ℹ️"}
            print(f"  {sev_icon.get(p.severity, '📋')} {p.name}")
            print(f"      {p.description}")
            print(f"      💡 {p.suggestion}")
            print()
        return

    if args.file:
        if args.json:
            result = detector.analyze(detector.scan_file(args.file))
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            matches = detector.scan_file(args.file)
            _print_matches(matches)
        return

    if args.text:
        if args.json:
            result = detector.analyze(args.text)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            matches = detector.scan(args.text)
            _print_matches(matches)
        return

    parser.print_help()


def _print_matches(matches):
    """打印可读的检测结果。"""
    if not matches:
        print("✅ 未检测到已知逻辑谬误")
        return

    sev_icons = {"high": "🔴", "medium": "🟡", "low": "ℹ️"}
    print(f"检测到 {len(matches)} 个逻辑谬误:\n")

    for i, m in enumerate(matches, 1):
        print(f"{sev_icons.get(m.severity, '📋')} [{i}] {m.fallacy}")
        print(f"    匹配: 「{m.matched_text}」")
        print(f"    上下文: ...{m.context}...")
        print(f"    建议: {m.suggestion}")
        print()


if __name__ == "__main__":
    main()
