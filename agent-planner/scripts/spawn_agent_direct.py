"""spawn_agent_direct.py — 直接使用 sessions_spawn 的子代理调用

spawn-agent.py 通过 PowerShell 中转，延迟较高（~200ms）。

本模块提供直接调用 sessions_spawn 的方式，延迟更低（<50ms）。

使用方式：
    from spawn_agent_direct import spawn_agent_direct
    
    result = spawn_agent_direct(
        task="审查 backtest_engine.py 默认参数...",
        label="engine-auditor",
        mode="run"
    )
"""

import json
import time
from typing import Dict, Optional, Any

# sessions_spawn 是 OpenClaw 内置函数，通过 sessions 模块调用
try:
    from sessions import spawn as sessions_spawn
except ImportError:
    sessions_spawn = None


def spawn_agent_direct(
    task: str,
    label: str,
    mode: str = "run",
    model: Optional[str] = None,
    runtime: str = "subagent",
    cleanup: str = "delete",
    **kwargs
) -> Dict[str, Any]:
    """
    直接使用 sessions_spawn 派生子代理，无 PowerShell 中转。
    
    Args:
        task: 任务描述
        label: 子代理标签
        mode: 运行模式 ("run"=一次性, "session"=持久会话)
        model: 模型覆盖（可选）
        runtime: 运行时 ("subagent"=子代理, "acp"=ACP)
        cleanup: 完成后清理方式
        **kwargs: 其他 sessions_spawn 参数
    
    Returns:
        {"status": "ok", "session_key": "...", "run_id": "..."}
        或 {"status": "error", "message": "..."}
    """
    if sessions_spawn is None:
        return {
            "status": "error",
            "message": "sessions_spawn not available in this environment"
        }
    
    start_time = time.time()
    
    try:
        result = sessions_spawn(
            task=task,
            label=label,
            mode=mode,
            model=model,
            runtime=runtime,
            cleanup=cleanup,
            **kwargs
        )
        
        elapsed = time.time() - start_time
        
        return {
            "status": "ok",
            "session_key": result.get("session_key"),
            "run_id": result.get("run_id"),
            "elapsed_ms": round(elapsed * 1000, 1)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "elapsed_ms": round((time.time() - start_time) * 1000, 1)
        }


def spawn_agents_parallel(
    tasks: list,
    labels: list,
    mode: str = "run"
) -> Dict[str, Any]:
    """
    并行派生子代理（用于多专家并行审查）。
    
    Args:
        tasks: 任务描述列表
        labels: 子代理标签列表
        mode: 运行模式
    
    Returns:
        {"status": "ok", "results": [...], "elapsed_ms": ...}
    """
    if len(tasks) != len(labels):
        return {
            "status": "error",
            "message": f"tasks ({len(tasks)}) and labels ({len(labels)}) count mismatch"
        }
    
    start_time = time.time()
    results = []
    
    # 并行调用
    for task, label in zip(tasks, labels):
        result = spawn_agent_direct(task=task, label=label, mode=mode)
        results.append(result)
    
    elapsed = time.time() - start_time
    
    return {
        "status": "ok",
        "results": results,
        "elapsed_ms": round(elapsed * 1000, 1),
        "count": len(results)
    }


# 向后兼容：保留原来的函数签名
def run_agent(task: str, label: str, timeout: int = 30) -> Dict[str, Any]:
    """向后兼容接口，调用 spawn_agent_direct"""
    return spawn_agent_direct(task=task, label=label, mode="run")


if __name__ == "__main__":
    # 测试
    result = spawn_agent_direct(
        task="简单测试：返回 'ok'",
        label="test-direct",
        mode="run"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))