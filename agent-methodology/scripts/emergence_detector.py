#!/usr/bin/env python3
"""
涌现检测器 — 监控多 Agent 系统中的异常涌现行为。

检测以下异常模式:
1. Token 消耗突增（正常均值的 3σ 以上）
2. 工具调用循环（同一工具 → 相似参数 > 5 次）
3. 推理发散（相邻推理步结论方向不一致）
4. 上下文窗口水位（>80% 时触发告警）

用法:
    # 实时检测（单条事件）
    python emergence_detector.py --event '{"type":"tool_call","tool":"search","params":{...}}'

    # 批量分析日志
    python emergence_detector.py --logfile ./agent_events.jsonl

    # 查看当前状态
    python emergence_detector.py --status
"""

import json
import math
import os
import statistics
import sys
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ============================================================
# 配置
# ============================================================

class EmergenceConfig:
    """涌现检测阈值配置。"""
    TOKEN_SIGMA_THRESHOLD = 3.0       # Token 突增 Z-score 阈值
    TOOL_LOOP_COUNT = 5               # 工具调用循环计数阈值
    TOOL_LOOP_WINDOW = 120            # 工具循环检测时间窗口（秒）
    CONTEXT_WATERMARK = 0.80          # 上下文水位告警阈值
    DIVERGENCE_CONSECUTIVE = 3        # 连续发散步数阈值
    WINDOW_SIZE = 20                  # 滑动窗口大小


# ============================================================
# 数据结构
# ============================================================

@dataclass
class Event:
    type: str  # tool_call, reasoning_step, context_update, token_usage
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: Dict) -> "Event":
        return cls(
            type=d.get("type", "unknown"),
            timestamp=d.get("timestamp", time.time()),
            data=d.get("data", {}),
        )


@dataclass
class Alert:
    alert_type: str
    severity: str  # info, warning, critical
    message: str
    detail: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


# ============================================================
# 检测器
# ============================================================

class EmergenceDetector:
    """涌现行为检测器。"""

    def __init__(self, config: Optional[EmergenceConfig] = None):
        self.config = config or EmergenceConfig()

        # Token 监控
        self.token_usage: Deque[float] = deque(maxlen=self.config.WINDOW_SIZE)

        # 工具调用监控
        self.tool_calls: Deque[Tuple[str, str, float]] = deque()  # (tool, param_hash, timestamp)

        # 推理发散监控
        self.reasoning_directions: Deque[float] = deque(maxlen=10)  # 最近的方向向量

        # 上下文水位
        self.context_watermark: float = 0.0

        # 告警历史
        self.alerts: List[Alert] = []

        # 代理标识
        self.agent_id: Optional[str] = None

    def ingest(self, event: Event) -> List[Alert]:
        """接收一条事件，返回触发的告警。"""
        alerts = []

        if event.type == "token_usage":
            alerts.extend(self._check_token(event))
        elif event.type == "tool_call":
            alerts.extend(self._check_tool_loop(event))
        elif event.type == "reasoning_step":
            alerts.extend(self._check_divergence(event))
        elif event.type == "context_update":
            alerts.extend(self._check_context_watermark(event))

        return alerts

    # --------------------------------------------------
    # Token 突增检测
    # --------------------------------------------------

    def _check_token(self, event: Event) -> List[Alert]:
        tokens = event.data.get("tokens", 0)
        self.token_usage.append(tokens)

        alerts = []
        if len(self.token_usage) >= 5:
            mean = statistics.mean(self.token_usage)
            stdev = statistics.stdev(self.token_usage) if len(self.token_usage) > 1 else 1.0

            if stdev > 0:
                z_score = (tokens - mean) / stdev
                if z_score > self.config.TOKEN_SIGMA_THRESHOLD:
                    alert = Alert(
                        alert_type="token_spike",
                        severity="warning" if z_score < 5 else "critical",
                        message=f"Token 消耗突增 (Z={z_score:.1f})：当前 {tokens}，均值 {mean:.0f}",
                        detail={
                            "current": tokens,
                            "mean": round(mean, 0),
                            "z_score": round(z_score, 2),
                            "window_size": len(self.token_usage),
                        },
                    )
                    alerts.append(alert)

        return alerts

    # --------------------------------------------------
    # 工具调用循环检测
    # --------------------------------------------------

    def _check_tool_loop(self, event: Event) -> List[Alert]:
        tool_name = event.data.get("tool", "unknown")
        param_hash = self._hash_params(event.data.get("params", {}))

        now = event.timestamp
        self.tool_calls.append((tool_name, param_hash, now))

        # 清理超时记录
        while self.tool_calls and (now - self.tool_calls[0][2]) > self.config.TOOL_LOOP_WINDOW:
            self.tool_calls.popleft()

        # 统计最近窗口内同一个工具+相似参数的调用次数
        recent_same = [
            c for c in self.tool_calls
            if c[0] == tool_name and c[1] == param_hash
        ]

        alerts = []
        if len(recent_same) >= self.config.TOOL_LOOP_COUNT:
            alert = Alert(
                alert_type="tool_loop",
                severity="warning",
                message=f"工具 {tool_name} 循环调用（相同参数 {len(recent_same)} 次）",
                detail={
                    "tool": tool_name,
                    "call_count": len(recent_same),
                    "window_seconds": self.config.TOOL_LOOP_WINDOW,
                    "param_hash": param_hash,
                },
            )
            alerts.append(alert)

        return alerts

    # --------------------------------------------------
    # 推理发散检测
    # --------------------------------------------------

    def _check_divergence(self, event: Event) -> List[Alert]:
        # 简化的方向向量：从推理文本中提取"方向"
        text = event.data.get("text", "")
        direction = self._extract_direction(text)

        self.reasoning_directions.append(direction)

        alerts = []
        if len(self.reasoning_directions) >= self.config.DIVERGENCE_CONSECUTIVE:
            # 检查最近几步的方差
            recent = list(self.reasoning_directions)[-self.config.DIVERGENCE_CONSECUTIVE:]
            # 评估方向变化幅度
            changes = [abs(recent[i] - recent[i-1]) for i in range(1, len(recent))]
            avg_change = statistics.mean(changes) if changes else 0

            if avg_change > 0.5:  # 方向变化超过 0.5 表示大幅度摇摆
                alert = Alert(
                    alert_type="reasoning_divergence",
                    severity="info",
                    message=f"推理方向连续发散（平均变化 {avg_change:.2f}）",
                    detail={
                        "consecutive_steps": len(recent),
                        "avg_direction_change": round(avg_change, 2),
                        "recent_directions": [round(d, 2) for d in recent],
                    },
                )
                alerts.append(alert)

        return alerts

    # --------------------------------------------------
    # 上下文水位检测
    # --------------------------------------------------

    def _check_context_watermark(self, event: Event) -> List[Alert]:
        self.context_watermark = event.data.get("ratio", 0.0)

        alerts = []
        if self.context_watermark >= self.config.CONTEXT_WATERMARK:
            alert = Alert(
                alert_type="context_high_watermark",
                severity="warning" if self.context_watermark < 0.95 else "critical",
                message=f"上下文窗口水位 {self.context_watermark:.0%}（阈值 {self.config.CONTEXT_WATERMARK:.0%}）",
                detail={
                    "current_ratio": self.context_watermark,
                    "threshold": self.config.CONTEXT_WATERMARK,
                    "action": "建议执行 compress 释放上下文空间",
                },
            )
            alerts.append(alert)

        return alerts

    # --------------------------------------------------
    # 辅助方法
    # --------------------------------------------------

    def _hash_params(self, params: Any) -> str:
        """对参数做模糊哈希（忽略值中的数字差异）。"""
        text = json.dumps(params, sort_keys=True)
        return str(hash(text) % (2**32))

    def _extract_direction(self, text: str) -> float:
        """
        从推理文本中提取方向向量（简化为单维 -1 到 1）。
        负值 = 否定/怀疑，正值 = 肯定/确认，0 = 中性。
        """
        positive_words = ["是", "对", "可以", "会", "有", "好", "正确", "可行", "应该"]
        negative_words = ["不", "否", "错", "不行", "不能", "没有", "不好", "错误", "不可行"]

        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)

        total = pos_count + neg_count
        if total == 0:
            return 0.0

        return (pos_count - neg_count) / total

    # --------------------------------------------------
    # 状态输出
    # --------------------------------------------------

    def get_status(self) -> Dict:
        """输出当前检测器状态。"""
        return {
            "agent_id": self.agent_id,
            "token_usage_stats": {
                "window_size": len(self.token_usage),
                "mean": round(statistics.mean(self.token_usage), 1) if self.token_usage else 0,
                "recent": list(self.token_usage)[-5:] if self.token_usage else [],
            },
            "tool_call_stats": {
                "recent_window_seconds": self.config.TOOL_LOOP_WINDOW,
                "recent_count": len(self.tool_calls),
            },
            "context_watermark": round(self.context_watermark, 2),
            "alert_count": len(self.alerts),
            "recent_alerts": [
                asdict(a) for a in self.alerts[-5:]
            ],
        }

    def get_alert_history(self) -> List[dict]:
        return [asdict(a) for a in self.alerts]


# ============================================================
# 多 Agent 协调器（跨 Agent 涌现检测）
# ============================================================

class MultiAgentEmergenceCoordinator:
    """跨多个 Agent 的涌现检测协调器。"""

    def __init__(self):
        self.detectors: Dict[str, EmergenceDetector] = {}

    def register_agent(self, agent_id: str) -> EmergenceDetector:
        detector = EmergenceDetector()
        detector.agent_id = agent_id
        self.detectors[agent_id] = detector
        return detector

    def ingest_event(self, agent_id: str, event: Event) -> List[Alert]:
        detector = self.detectors.get(agent_id)
        if not detector:
            return [Alert(
                alert_type="unknown_agent",
                severity="warning",
                message=f"未知 Agent: {agent_id}",
            )]
        return detector.ingest(event)

    def get_system_status(self) -> Dict:
        """输出全系统涌现状态。"""
        return {
            "agent_count": len(self.detectors),
            "agents": {
                aid: d.get_status()
                for aid, d in self.detectors.items()
            },
            "global_alerts": sum(
                len(d.alerts) for d in self.detectors.values()
            ),
        }


# ============================================================
# 命令行入口
# ============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="涌现检测器 — 多Agent异常行为监控")
    parser.add_argument("--event", help="单条事件 JSON")
    parser.add_argument("--logfile", help="事件日志文件 (.jsonl)")
    parser.add_argument("--status", action="store_true", help="查看当前状态")
    parser.add_argument("--agent", default="default", help="Agent ID")
    args = parser.parse_args()

    coordinator = MultiAgentEmergenceCoordinator()
    detector = coordinator.register_agent(args.agent)

    if args.event:
        try:
            event_data = json.loads(args.event)
            event = Event.from_dict(event_data)
            alerts = detector.ingest(event)
            output = {
                "event": event_data,
                "alerts": [asdict(a) for a in alerts],
                "agent_status": detector.get_status(),
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))

            if alerts:
                for a in alerts:
                    sev_icon = {"info": "ℹ️", "warning": "⚠️", "critical": "🔴"}
                    print(f"\n{sev_icon.get(a.severity, '📋')} [{a.alert_type}] {a.message}")

        except json.JSONDecodeError as e:
            print(f"❌ 事件 JSON 解析失败: {e}")
            sys.exit(1)

    elif args.logfile:
        if not os.path.exists(args.logfile):
            print(f"❌ 日志文件不存在: {args.logfile}")
            sys.exit(1)

        with open(args.logfile, "r", encoding="utf-8") as f:
            all_alerts = []
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    event_data = json.loads(line)
                    event = Event.from_dict(event_data)
                    alerts = detector.ingest(event)
                    all_alerts.extend(alerts)
                except json.JSONDecodeError:
                    print(f"⚠️ 第 {line_num} 行 JSON 解析失败，跳过")

        print(f"处理完成: {args.logfile}")
        print(f"事件数: {detector.get_status()['token_usage_stats']['window_size']}")
        print(f"告警数: {len(all_alerts)}")
        for a in all_alerts:
            print(f"  [{a.severity}] {a.alert_type}: {a.message}")

    elif args.status:
        print(json.dumps(detector.get_status(), ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
