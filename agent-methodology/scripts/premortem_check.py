#!/usr/bin/env python3
"""
预验尸检查脚本 — 在执行重要操作前，假设已失败，回溯推导失败原因。

用法:
    python premortem_check.py --task "将要执行的操作描述"
    python premortem_check.py --task "修改 config.yml 并重启服务" --verbose

输出:
    风险清单 + 严重度评级 + fallback 链路建议
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class Risk:
    step: str
    scenario: str
    severity: str  # L1-L4
    probability: str  # 高/中/低
    fallback: str
    prevention: str = ""


# 已知识别模式库：操作类型 → 典型失败模式
KNOWN_FAILURE_PATTERNS = [
    {
        "pattern": r"修改.*(config|配置文件|yml|yaml|json|toml|ini)",
        "risks": [
            Risk("修改配置文件", "格式错误导致服务无法启动", "L2", "中",
                 "修改前备份原文件，修改后用 linter 验证",
                 "先备份再修改，修改后执行语法检查"),
            Risk("修改配置文件", "遗漏关键配置项导致功能异常", "L2", "中",
                 "对比新旧 diff，逐项确认",
                 "修改后运行相关功能测试"),
        ],
    },
    {
        "pattern": r"(删除|移除|rm|del).*(文件|目录|folder)",
        "risks": [
            Risk("删除操作", "误删生产环境有效文件", "L3", "高",
                 "立即停止操作，从 git/备份恢复",
                 "先确认路径是否正确，使用回收站/trash 而非直接删除"),
            Risk("删除操作", "删除后依赖该文件的程序崩溃", "L2", "中",
                 "检查文件引用关系，确认无依赖后再删除",
                 "先用 grep 检查文件引用"),
        ],
    },
    {
        "pattern": r"(部署|发布|deploy|release)",
        "risks": [
            Risk("部署操作", "新版本引入回归 Bug", "L3", "中",
                 "保留旧版本，执行快速回滚",
                 "先在小范围灰度发布，监控 10 分钟"),
            Risk("部署操作", "数据库迁移失败导致数据不一致", "L4", "低",
                 "执行数据库回滚脚本修复",
                 "先在 staging 环境执行完整迁移流程"),
        ],
    },
    {
        "pattern": r"(重构|refactor|重写|rewrite)",
        "risks": [
            Risk("代码重构", "功能行为改变影响下游调用方", "L3", "高",
                 "保留旧接口做兼容，逐步切换",
                 "重构前确保测试覆盖率 > 80%"),
            Risk("代码重构", "删除看似无用但实际在用的代码", "L2", "中",
                 "从 git history 恢复被删代码",
                 "先用 grep 全项目搜索引用"),
        ],
    },
    {
        "pattern": r"(数据库|db|migration|schema|DDL)",
        "risks": [
            Risk("数据库操作", "DDL 锁表导致线上延迟", "L4", "中",
                 "终止长时间运行的查询，回滚 DDL",
                 "使用 pt-online-schema-change 或 gh-ost"),
            Risk("数据库操作", "数据列类型变更导致应用崩溃", "L4", "高",
                 "立即回滚 DDL，通知相关团队",
                 "先在 staging 测试所有使用该列的查询"),
        ],
    },
    {
        "pattern": r"(API|接口|endpoint|路由|route)",
        "risks": [
            Risk("接口变更", "返回格式变化导致客户端解析失败", "L3", "高",
                 "恢复旧接口，用版本号区分新旧",
                 "先增加新接口，旧接口保留一个 deprecation 周期"),
            Risk("接口变更", "鉴权方式变化导致大量 401", "L4", "高",
                 "回滚鉴权配置，通知客户端更新",
                 "分阶段灰度切换鉴权方式"),
        ],
    },
    {
        "pattern": r"(npm|pip|gem|nuget|maven|包|依赖|dependency|upgrade|update)",
        "risks": [
            Risk("依赖升级", "新版本不兼容导致构建失败", "L2", "中",
                 "锁定回旧版本，排查 Breaking Changes",
                 "先查看 CHANGELOG 中的 Breaking Changes"),
            Risk("依赖升级", "依赖引入安全漏洞", "L3", "低",
                 "降级到安全版本，报告安全团队",
                 "升级前先查 CVE 数据库"),
        ],
    },
]


def match_known_patterns(task: str) -> List[Risk]:
    """匹配已知故障模式库。"""
    risks = []
    for pattern_def in KNOWN_FAILURE_PATTERNS:
        if re.search(pattern_def["pattern"], task, re.IGNORECASE):
            risks.extend(pattern_def["risks"])
    return risks


def generate_generic_risks(task: str) -> List[Risk]:
    """生成通用风险项。"""
    generic_risks = []

    # 通用：不兼容变更
    generic_risks.append(Risk(
        "通用检查", "变更导致已有功能行为变化",
        "L2", "低",
        "保留旧行为兼容层，逐步迁移",
        "变更前梳理所有受影响的功能路径"
    ))

    # 通用：文档/沟通缺失
    generic_risks.append(Risk(
        "通用检查", "变更未通知相关方导致协同问题",
        "L1", "中",
        "补充沟通",
        "变更前在团队频道发布变更通知"
    ))

    # 通用：验证不足
    generic_risks.append(Risk(
        "通用检查", "未充分测试导致遗漏场景",
        "L2", "中",
        "补充测试用例后重新验证",
        "变更后运行相关测试套件"
    ))

    return generic_risks


def determine_overall_level(risks: List[Risk]) -> str:
    """根据风险列表确定总体风险等级。"""
    severity_order = {"L1": 1, "L2": 2, "L3": 3, "L4": 4}
    max_sev = max((severity_order.get(r.severity, 0) for r in risks), default=0)
    return f"L{max_sev}" if max_sev > 0 else "L1"


def main():
    parser = argparse.ArgumentParser(description="预验尸检查 — 执行前风险预判")
    parser.add_argument("--task", required=True, help="将要执行的操作描述")
    parser.add_argument("--plan", help="计划文件路径（可选）")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    # 1. 匹配已知模式
    known_risks = match_known_patterns(args.task)

    # 2. 生成通用风险
    generic_risks = generate_generic_risks(args.task)

    # 3. 合并去重
    all_risks = known_risks + generic_risks

    # 去重：相同 step + scenario 只保留第一个
    seen = set()
    unique_risks = []
    for r in all_risks:
        key = (r.step, r.scenario)
        if key not in seen:
            seen.add(key)
            unique_risks.append(r)

    # 4. 按严重度排序
    severity_order = {"L4": 0, "L3": 1, "L2": 2, "L1": 3}
    unique_risks.sort(key=lambda r: severity_order.get(r.severity, 99))

    overall_level = determine_overall_level(unique_risks)

    # 5. 输出
    result = {
        "task": args.task,
        "overall_risk_level": overall_level,
        "risk_count": len(unique_risks),
        "risks": [asdict(r) for r in unique_risks],
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"任务: {args.task}")
        print(f"总体风险等级: {overall_level}")
        print(f"风险项数: {len(unique_risks)}")
        print()
        for i, r in enumerate(unique_risks, 1):
            print(f"[{i}] {r.step}")
            print(f"    场景: {r.scenario}")
            print(f"    严重度: {r.severity} | 概率: {r.probability}")
            print(f"    Fallback: {r.fallback}")
            if args.verbose and r.prevention:
                print(f"    预防措施: {r.prevention}")
            print()

        if overall_level in ("L3", "L4"):
            print("⚠️  高风险任务，建议走完整 System 2 团队路径")
        elif overall_level == "L2":
            print("ℹ️  中等风险，建议执行前确认 fallback 就绪")


if __name__ == "__main__":
    main()
