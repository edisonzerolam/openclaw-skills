#!/usr/bin/env python3
"""
多 Agent 协调仲裁器 — 跨 Agent 调度、置信度聚合、冲突仲裁。

核心职责:
1. 双系统路由：根据任务复杂度决定子 Agent 数量和方法论策略
2. 预验尸检查：派发前扫描全局风险
3. 置信度聚合：收集各 Agent 输出并加权融合
4. 冲突仲裁：当子 Agent 结论不一致时，自动裁决或标记分歧
5. 反馈收集：记录每轮执行的成功/失败模式

用法:
    # 单 Agent 调度（System 1）
    python agent_orchestrator.py --task "查茅台股价" --mode single

    # 多 Agent 并行（System 2）
    python agent_orchestrator.py --task "分析投资组合风险" --mode panel

    # 批量分析日志
    python agent_orchestrator.py --logfile ./agent_outputs.jsonl
"""

import argparse
import json
import statistics
import sys
import time
from dataclasses import dataclass, asdict, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ============================================================
# 数据结构
# ============================================================

@dataclass
class TaskDef:
    """任务定义。"""
    id: str = ""
    description: str = ""
    complexity: str = "L1"  # L1-L4
    required_domains: List[str] = field(default_factory=list)
    output_format: str = "markdown"
    user_context: str = ""


@dataclass
class AgentOutput:
    """单个 Agent 的输出。"""
    agent_id: str
    agent_type: str
    conclusion: str
    confidence: float  # 0-1
    reasoning: str = ""
    sources: List[str] = field(default_factory=list)
    uncertainty_notes: str = ""
    elapsed: float = 0.0
    status: str = "success"  # success, partial, failed


@dataclass
class AggregatedResult:
    """聚合后的最终结果。"""
    task_id: str
    consensus: str  # 最终结论
    consensus_confidence: float  # 0-1
    consensus_level: str  # unanimous, majority, split, single
    agent_outputs: List[AgentOutput] = field(default_factory=list)
    disagreements: List[Dict] = field(default_factory=list)


# ============================================================
# 置信度聚合器
# ============================================================

class ConfidenceAggregator:
    """跨 Agent 置信度聚合。"""

    @staticmethod
    def weighted_average(outputs: List[AgentOutput]) -> Tuple[float, str]:
        """
        加权平均聚合。
        权重 = 置信度本身（高置信度的 Agent 有更大话语权）。
        """
        if not outputs:
            return 0.0, "no_agents"

        successful = [o for o in outputs if o.status == "success"]
        if not successful:
            return 0.0, "all_failed"

        weights = [o.confidence for o in successful]
        total_weight = sum(weights)

        # 对结论做简单聚类：按结论文本的相似性分组
        # 简化实现：直接取最高置信度的结论为最终结论
        best = max(successful, key=lambda o: o.confidence)

        # 检测分歧
        high_conf = [o for o in successful if o.confidence >= 0.7]
        low_conf = [o for o in successful if o.confidence < 0.7]

        if len(high_conf) == len(successful):
            consensus_level = "unanimous"
        elif len(high_conf) >= len(successful) / 2:
            consensus_level = "majority"
        elif len(high_conf) > 0:
            consensus_level = "split"
        else:
            consensus_level = "low_confidence"

        # 加权平均置信度
        avg_confidence = sum(o.confidence * o.confidence for o in successful) / max(total_weight, 0.01)
        avg_confidence = max(0.0, min(1.0, avg_confidence))

        return avg_confidence, consensus_level

    @staticmethod
    def find_disagreements(outputs: List[AgentOutput]) -> List[Dict]:
        """识别 Agent 之间的结论分歧。"""
        disagreements = []
        for i, a in enumerate(outputs):
            for j, b in enumerate(outputs):
                if i >= j:
                    continue
                if a.status != "success" or b.status != "success":
                    continue

                # 置信度差距 > 0.4 标记为显著分歧
                conf_gap = abs(a.confidence - b.confidence)
                if conf_gap > 0.4:
                    disagreements.append({
                        "agents": (a.agent_id, b.agent_id),
                        "confidence_gap": round(conf_gap, 2),
                        "higher": a.agent_id if a.confidence > b.confidence else b.agent_id,
                        "lower": b.agent_id if a.confidence > b.confidence else a.agent_id,
                    })

        return disagreements


# ============================================================
# 协调仲裁器
# ============================================================

class AgentOrchestrator:
    """
    多 Agent 协调仲裁器。

    工作流:
    1. 接收任务 → 判断复杂度 → 选择 Agent 阵容
    2. 预验尸 → 全局风险扫描
    3. 派发任务到各 Agent
    4. 收集输出 → 置信度聚合
    5. 冲突仲裁
    6. 输出最终结果
    """

    def __init__(self):
        self.aggregator = ConfidenceAggregator()
        self.execution_log: List[Dict] = []
        self.route_counter: Dict[str, int] = {}  # System 1/2 计数

    def orchestrate(self, task: TaskDef,
                    agent_pool: Optional[List[str]] = None) -> AggregatedResult:
        """
        执行完整编排流程。

        参数:
            task: 任务定义
            agent_pool: 可用 Agent 类型列表（默认自动选择）
        """
        start_time = time.time()
        task.id = f"task_{int(start_time)}"

        # ============================================================
        # Step 1: 双系统路由
        # ============================================================
        system, agent_count = self._route_task(task)
        self.route_counter[system] = self.route_counter.get(system, 0) + 1

        # ============================================================
        # Step 2: 预验尸
        # ============================================================
        risks = self._global_premortem(task, system)

        # ============================================================
        # Step 3: 选择 Agent 阵容
        # ============================================================
        agents = self._select_agents(task, agent_count, agent_pool)

        if not agents:
            return AggregatedResult(
                task_id=task.id,
                consensus="",
                consensus_confidence=0.0,
                consensus_level="no_agents_available",
                agent_outputs=[],
                disagreements=[],
            )

        # ============================================================
        # Step 4: 派发 + 收集（实际调用由主调度器完成）
        # ============================================================
        # 这里仅供框架示意，真实的 agent 调用在上层完成
        # 本类提供数据结构和方法论支持

        return AggregatedResult(
            task_id=task.id,
            consensus="",
            consensus_confidence=0.0,
            consensus_level="pending_execution",
            agent_outputs=[],
            disagreements=[],
        )

    # --------------------------------------------------
    # 双系统路由
    # --------------------------------------------------

    def _route_task(self, task: TaskDef) -> Tuple[str, int]:
        """
        根据复杂度决定路由策略：
        - L1: System 1, 单 Agent
        - L2: System 1 → 快速模板匹配
        - L3: System 2, 3-5 Agent 并行
        - L4: System 2, 5-8 Agent 完整团队
        """
        routing = {
            "L1": ("System 1", 1),
            "L2": ("System 1", 1),
            "L3": ("System 2", 4),
            "L4": ("System 2", 6),
        }
        return routing.get(task.complexity, ("System 1", 1))

    # --------------------------------------------------
    # 全局预验尸
    # --------------------------------------------------

    def _global_premortem(self, task: TaskDef, system: str) -> List[Dict]:
        """在 Agent 派发前执行全局预验尸。"""
        risks = []

        if system == "System 2" and not task.required_domains:
            risks.append({
                "type": "domain_undefined",
                "severity": "L2",
                "message": "System 2 任务缺少领域定义，可能导致 Agent 选择偏差",
                "mitigation": "补充 task.required_domains 字段",
            })

        if len(task.description) < 20:
            risks.append({
                "type": "task_too_vague",
                "severity": "L2",
                "message": "任务描述过短（<20字），Agent 可能理解偏差",
                "mitigation": "使用 5W2H 框架补充任务描述",
            })

        # 记录预验尸日志
        self.execution_log.append({
            "phase": "premortem",
            "task_id": task.id,
            "risks": risks,
            "timestamp": time.time(),
        })

        return risks

    # --------------------------------------------------
    # Agent 阵容选择
    # --------------------------------------------------

    def _select_agents(self, task: TaskDef, count: int,
                       pool: Optional[List[str]]) -> List[str]:
        """根据任务领域选择最佳 Agent 阵容。"""
        if pool:
            return pool[:count]

        # 默认 Agent 映射
        domain_agent_map = {
            "金融投资": ["market-strategist", "risk-manager", "valuation-expert"],
            "技术工程": ["debug-expert", "code-reviewer", "general"],
            "内容创作": ["article-writer", "general"],
            "数据分析": ["general"],
            "综合": ["general"],
            "法务": ["legal-researcher", "risk-manager"],
        }

        agents = []
        for domain in task.required_domains:
            candidates = domain_agent_map.get(domain, ["general"])
            agents.extend(candidates[:count])

        # 去重
        seen = set()
        unique = []
        for a in agents:
            if a not in seen:
                seen.add(a)
                unique.append(a)

        return unique[:count] if unique else ["general"]

    # --------------------------------------------------
    # 结果聚合
    # --------------------------------------------------

    def aggregate(self, outputs: List[AgentOutput]) -> AggregatedResult:
        """聚合多 Agent 输出。"""
        if not outputs:
            return AggregatedResult(
                task_id="",
                consensus="无输出",
                consensus_confidence=0.0,
                consensus_level="empty",
                agent_outputs=[],
                disagreements=[],
            )

        # 置信度加权聚合
        avg_conf, level = self.aggregator.weighted_average(outputs)

        # 识别分歧
        disagreements = self.aggregator.find_disagreements(outputs)

        # 选择最终结论：最高置信度的成功 Agent 输出
        successful = [o for o in outputs if o.status == "success"]
        if successful:
            best = max(successful, key=lambda o: o.confidence)
            final_consensus = best.conclusion
        else:
            final_consensus = "所有 Agent 均失败"

        result = AggregatedResult(
            task_id=f"agg_{int(time.time())}",
            consensus=final_consensus,
            consensus_confidence=round(avg_conf, 2),
            consensus_level=level,
            agent_outputs=outputs,
            disagreements=disagreements,
        )

        # 记录到执行日志
        self.execution_log.append({
            "phase": "aggregation",
            "task_id": result.task_id,
            "consensus_level": level,
            "confidence": avg_conf,
            "disagreement_count": len(disagreements),
            "timestamp": time.time(),
        })

        return result

    # --------------------------------------------------
    # 状态输出
    # --------------------------------------------------

    def get_status(self) -> Dict:
        """输出编排器状态。"""
        return {
            "route_counts": self.route_counter,
            "total_executions": sum(self.route_counter.values()),
            "execution_log_count": len(self.execution_log),
        }

    def to_json(self) -> str:
        return json.dumps({"orchestrator": self.get_status()}, ensure_ascii=False, indent=2)


# ============================================================
# 命令行入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="多 Agent 协调仲裁器 — 调度+聚合+仲裁")
    parser.add_argument("--task", help="任务描述")
    parser.add_argument("--mode", choices=["single", "panel", "team"],
                        default="single", help="执行模式")
    parser.add_argument("--complexity", choices=["L1", "L2", "L3", "L4"],
                        default="L1", help="任务复杂度")
    parser.add_argument("--domains", nargs="*", default=[],
                        help="所需领域（如 金融投资 技术工程）")
    parser.add_argument("--logfile", help="批量分析 Agent 输出日志 (.jsonl)")
    parser.add_argument("--status", action="store_true", help="查看编排器状态")
    parser.add_argument("--demo", action="store_true", help="运行演示模式")
    args = parser.parse_args()

    orchestrator = AgentOrchestrator()

    if args.status:
        print(orchestrator.to_json())
        return

    if args.demo:
        print("=" * 60)
        print("Agent Orchestrator 演示")
        print("=" * 60)

        # 模拟 3 个 Agent 的输出
        outputs = [
            AgentOutput(
                agent_id="agent-1", agent_type="researcher-ds",
                conclusion="方案 A 风险较低，建议优先执行",
                confidence=0.85, reasoning="基于历史回测数据", status="success",
            ),
            AgentOutput(
                agent_id="agent-2", agent_type="risk-manager",
                conclusion="方案 A 尾部风险偏高，建议方案 B",
                confidence=0.65, reasoning="压力测试显示最大回撤超标", status="success",
            ),
            AgentOutput(
                agent_id="agent-3", agent_type="market-strategist",
                conclusion="方案 A 的收益风险比更优",
                confidence=0.78, reasoning="夏普比率 1.8 vs 1.2", status="success",
            ),
        ]

        print("\n[1/3] 单 Agent 路由演示")
        task = TaskDef(description=args.task or "分析投资方案",
                       complexity=args.complexity or "L3",
                       required_domains=args.domains or ["金融投资"])
        system, count = orchestrator._route_task(task)
        risks = orchestrator._global_premortem(task, system)
        agents = orchestrator._select_agents(task, count, None)
        print(f"  复杂度: {task.complexity} → {system}")
        print(f"  Agent 阵容: {agents}")
        print(f"  预验尸风险: {len(risks)} 项")
        if risks:
            for r in risks:
                print(f"    [{r['severity']}] {r['message']}")

        print("\n[2/3] 多 Agent 置信度聚合演示")
        result = orchestrator.aggregate(outputs)
        print(f"  一致性: {result.consensus_level}")
        print(f"  聚合置信度: {result.consensus_confidence:.0%}")
        print(f"  最终结论: {result.consensus}")

        if result.disagreements:
            print(f"\n[3/3] 分歧检测: {len(result.disagreements)} 处")
            for d in result.disagreements:
                print(f"  Agent {d['agents'][0]} vs {d['agents'][1]}")
                print(f"  置信度差距: {d['confidence_gap']:.0%}")
                print(f"  更高置信度: {d['higher']}")

        print(f"\n编排器状态: {json.dumps(orchestrator.get_status(), ensure_ascii=False)}")
        print("=" * 60)
        return

    if args.logfile:
        # 批量分析日志 — 统计所有 Agent 输出的质量
        try:
            with open(args.logfile, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"❌ 日志文件不存在: {args.logfile}")
            sys.exit(1)

        outputs = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                output = AgentOutput(**{k: v for k, v in data.items()
                                        if k in AgentOutput.__dataclass_fields__})
                outputs.append(output)
            except (json.JSONDecodeError, TypeError):
                continue

        if not outputs:
            print("❌ 未解析到有效的 Agent 输出")
            sys.exit(1)

        result = orchestrator.aggregate(outputs)
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2,
                         default=str))
        return

    if args.task:
        task = TaskDef(
            description=args.task,
            complexity=args.complexity,
            required_domains=args.domains,
        )
        result = orchestrator.officiate(task)

        output = {
            "task": task.description,
            "complexity": task.complexity,
            "routing": orchestrator._route_task(task),
            "premortem_risks": orchestrator._global_premortem(task, "System 2" if task.complexity in ("L3", "L4") else "System 1"),
            "selected_agents": orchestrator._select_agents(task, 3, None),
            "orchestrator_status": orchestrator.get_status(),
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    parser.print_help()


# ============================================================
# 工具函数：生成兼容的 task prompt
# ============================================================

def build_subagent_prompt(task: TaskDef, agent_type: str,
                          methodology: bool = True) -> str:
    """
    构建注入方法论的 subagent prompt。
    与 subagent_injector.py 配合使用。
    """
    parts = [f"## 任务\n{task.description}"]

    if methodology:
        system = "System 2" if task.complexity in ("L3", "L4") else "System 1"
        parts.extend([
            f"\n## 思维模式：{system}",
            "### 输出置信度",
            "每个结论附带置信度标记：[高] > 0.9 / [中] 0.6-0.9 / [低] < 0.6",
            "### 预验尸检查",
            "开始前先想：如果这个任务会失败，最可能的原因是什么？",
        ])

    if task.user_context:
        parts.append(f"\n## 额外上下文\n{task.user_context}")

    parts.append(f"\n## 数据来源要求\n所有数据和结论必须有明确来源标注。")

    return "\n".join(parts)


if __name__ == "__main__":
    main()
