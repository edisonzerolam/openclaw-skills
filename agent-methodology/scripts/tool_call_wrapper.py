#!/usr/bin/env python3
"""
工具调用包装器 — 在每次工具调用外套上方法论层：
1. 预验尸：这个调用会怎么失败？
2. 执行：调用真实工具
3. 贝叶斯更新：根据结果更新置信度
4. 反馈循环：失败时分析根因 + 增益控制

用法（作为库引用）:
    from tool_call_wrapper import ToolCallWrapper
    wrapper = ToolCallWrapper()
    result = wrapper.call("read_file", {"path": "test.txt"})
"""

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, asdict, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ============================================================
# 增益控制器
# ============================================================

@dataclass
class StrategyState:
    """追踪某个工具/策略的健康状态。"""
    tool_name: str
    consecutive_failures: int = 0
    total_calls: int = 0
    success_calls: int = 0
    cooling: bool = False
    cooling_until: float = 0.0
    confidence: float = 0.5  # 初始中立

    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0.5
        return self.success_calls / self.total_calls


class GainController:
    """增益控制器 — 避免过调和欠调。"""

    COOLING_BASE_SECONDS = 30
    COOLING_MULTIPLIER = 2.0
    MAX_CONSECUTIVE_FAILURES = 3
    CONFIDENCE_DECAY = 0.15
    CONFIDENCE_BOOST = 0.05

    def __init__(self):
        self.states: Dict[str, StrategyState] = {}

    def _get_state(self, tool_name: str) -> StrategyState:
        if tool_name not in self.states:
            self.states[tool_name] = StrategyState(tool_name=tool_name)
        return self.states[tool_name]

    def record_success(self, tool_name: str):
        state = self._get_state(tool_name)
        state.total_calls += 1
        state.success_calls += 1
        state.consecutive_failures = 0
        state.confidence = min(state.confidence + GainController.CONFIDENCE_BOOST, 0.95)

    def record_failure(self, tool_name: str):
        state = self._get_state(tool_name)
        state.total_calls += 1
        state.consecutive_failures += 1
        state.confidence = max(state.confidence - GainController.CONFIDENCE_DECAY, 0.05)

        if state.consecutive_failures >= GainController.MAX_CONSECUTIVE_FAILURES:
            state.cooling = True
            cool_time = GainController.COOLING_BASE_SECONDS * (
                GainController.COOLING_MULTIPLIER ** (state.consecutive_failures - 3)
            )
            state.cooling_until = time.time() + cool_time

    def is_available(self, tool_name: str) -> Tuple[bool, Optional[str]]:
        """检查工具是否可用（不在冷却期）。"""
        state = self._get_state(tool_name)
        if state.cooling:
            remaining = state.cooling_until - time.time()
            if remaining > 0:
                return False, f"工具 {tool_name} 冷却中，剩余 {remaining:.0f}s"
            else:
                state.cooling = False
        return True, None

    def get_all_states(self) -> Dict[str, dict]:
        return {k: asdict(v) for k, v in self.states.items()}

    def to_json(self) -> str:
        return json.dumps({"strategies": self.get_all_states()}, ensure_ascii=False, indent=2)


# ============================================================
# 工具调用包装器
# ============================================================

class ToolCallWrapper:
    """在真实工具调用外层套方法论层。"""

    def __init__(self, gain_controller: Optional[GainController] = None):
        self.gc = gain_controller or GainController()

    def call(self, tool_name: str, params: Dict[str, Any],
             dry_run: bool = False) -> Dict[str, Any]:
        """
        带方法论的工具调用。

        参数:
            tool_name: 工具名称
            params: 工具参数
            dry_run: 仅预验尸，不执行

        返回:
            {
                "success": bool,
                "result": Any,
                "confidence": float,
                "premortem": {...},
                "feedback": {...}
            }
        """
        # ============================================================
        # Step 1: 可用性检查（增益控制）
        # ============================================================
        available, reason = self.gc.is_available(tool_name)
        if not available:
            return {
                "success": False,
                "result": None,
                "confidence": 0.0,
                "error": reason,
                "premortem": None,
                "feedback": None,
            }

        # ============================================================
        # Step 2: 预验尸
        # ============================================================
        premortem = self._premortem_check(tool_name, params)

        if dry_run:
            return {
                "success": True,
                "result": None,
                "confidence": 0.0,
                "premortem": premortem,
                "feedback": None,
                "dry_run": True,
            }

        # ============================================================
        # Step 3: 执行（调用真实函数）
        # ============================================================
        start_time = time.time()
        try:
            result = self._execute_tool(tool_name, params)
            elapsed = time.time() - start_time
            success = True
            error = None
        except Exception as e:
            elapsed = time.time() - start_time
            result = None
            success = False
            error = str(e)

        # ============================================================
        # Step 4: 贝叶斯更新置信度
        # ============================================================
        if success:
            self.gc.record_success(tool_name)
        else:
            self.gc.record_failure(tool_name)

        confidence = self.gc._get_state(tool_name).confidence

        # ============================================================
        # Step 5: 反馈循环 — 失败分析
        # ============================================================
        feedback = None
        if not success:
            feedback = self._analyze_failure(tool_name, params, error)

        return {
            "success": success,
            "result": result,
            "error": error,
            "confidence": round(confidence, 2),
            "elapsed": round(elapsed, 3),
            "premortem": premortem,
            "feedback": feedback,
        }

    # --------------------------------------------------
    # 预验尸检查（轻量版，调用前快速扫描）
    # --------------------------------------------------

    def _premortem_check(self, tool_name: str, params: Dict[str, Any]) -> Dict:
        """对本次工具调用做快速预验尸。"""
        risk_factors = []

        # 读操作风险低
        read_tools = {"read", "read_file", "get", "search", "grep", "glob", "list"}
        write_tools = {"write", "edit", "delete", "remove", "rename", "create", "patch"}

        if tool_name in write_tools:
            path = params.get("path", params.get("filePath", ""))
            risk_factors.append({
                "factor": "写操作",
                "detail": f"修改 {path}",
                "severity": "L2",
                "precaution": "修改前确认内容正确，准备好回退方案",
            })

        if "delete" in tool_name or "remove" in tool_name:
            path = params.get("path", "")
            risk_factors.append({
                "factor": "删除操作",
                "detail": f"删除 {path}",
                "severity": "L3",
                "precaution": "确认路径正确，确认无依赖引用",
            })

        if "exec" in tool_name or "bash" in tool_name or "command" in tool_name:
            cmd = params.get("command", "")
            if any(kw in cmd for kw in ["rm -rf", "drop", "format", "> /dev/" ]):
                risk_factors.append({
                    "factor": "高危命令",
                    "detail": f"执行: {cmd[:80]}...",
                    "severity": "L4",
                    "precaution": "确认环境非生产，确认命令语法",
                })

        return {
            "risks": risk_factors,
            "risk_level": max((r["severity"] for r in risk_factors), default="L1"),
        }

    # --------------------------------------------------
    # 真实执行（可被测试替换）
    # --------------------------------------------------

    def _execute_tool(self, tool_name: str, params: Dict[str, Any]):
        """
        执行真实工具调用。
        实际使用时，此方法应替换为真实的工具调用代码。
        这里提供一个可测试的模拟实现。
        """
        # 模拟：在测试环境中可以使用 mock
        # 生产环境中应替换为实际的 tool call
        raise NotImplementedError(
            f"请将 _execute_tool 替换为真实的 {tool_name} 调用"
        )

    # --------------------------------------------------
    # 失败分析（5Why 轻量版）
    # --------------------------------------------------

    def _analyze_failure(self, tool_name: str, params: Dict[str, Any],
                         error: str) -> Dict:
        """对失败做轻量根因分析。"""
        analysis = {
            "tool": tool_name,
            "error": error,
            "possible_causes": [],
            "suggestions": [],
        }

        # 常见错误模式匹配
        if "not found" in error.lower() or "no such" in error.lower():
            analysis["possible_causes"].append("路径或资源不存在")
            analysis["suggestions"].append("检查路径/名称是否正确")
            analysis["suggestions"].append("使用 glob/search 先确认存在性")

        elif "permission" in error.lower() or "denied" in error.lower():
            analysis["possible_causes"].append("权限不足")
            analysis["suggestions"].append("检查文件/目录权限")
            analysis["suggestions"].append("尝试以正确身份运行")

        elif "timeout" in error.lower() or "timed out" in error.lower():
            analysis["possible_causes"].append("操作超时")
            analysis["suggestions"].append("增加超时时间或拆分操作")
            analysis["suggestions"].append("检查目标是否可达")

        elif "invalid" in error.lower() or "syntax" in error.lower():
            analysis["possible_causes"].append("参数格式或语法错误")
            analysis["suggestions"].append("检查参数格式")
            analysis["suggestions"].append("先使用 dry-run 验证")

        else:
            analysis["possible_causes"].append(f"未知错误: {error[:100]}")
            analysis["suggestions"].append("检查输入参数是否正确")
            analysis["suggestions"].append("尝试简化操作后再试")

        return analysis


# ============================================================
# 命令行入口（用作独立检查）
# ============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="工具调用包装器 — 带方法论的调用")
    parser.add_argument("--tool", required=True, help="工具名称")
    parser.add_argument("--params", default="{}", help="JSON 参数")
    parser.add_argument("--dry-run", action="store_true", help="仅预验尸，不执行")
    parser.add_argument("--status", action="store_true", help="查看增益控制器状态")
    args = parser.parse_args()

    wrapper = ToolCallWrapper()

    if args.status:
        print(wrapper.gc.to_json())
        return

    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"❌ params 解析失败: {e}")
        sys.exit(1)

    result = wrapper.call(args.tool, params, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
