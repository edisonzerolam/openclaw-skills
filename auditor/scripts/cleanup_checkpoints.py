"""
cleanup_checkpoints.py — Checkpoint 清理模块

auditor v6.4+ 内置，作为 checkpoint 生命周期管理的一部分。

使用方式：
    from cleanup_checkpoints import cleanup_checkpoints, get_checkpoint_stats
    
    # 清理（保留最近 20 个 + 7 天内）
    removed = cleanup_checkpoints(
        checkpoint_dir=str(Path.home() / ".qclaw/skills/auditor/_checkpoints")
    )
    print(f"清理了 {removed} 个 checkpoint 文件")
    
    # 查看统计
    stats = get_checkpoint_stats(checkpoint_dir)
    print(stats)
"""

import json
import os
import re
import shutil
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple, Optional


# ============================================================
# 清理阈值配置
# ============================================================

MAX_CHECKPOINTS = 20          # 最大保留数量
MAX_AGE_DAYS = 7              # 最大保留天数
TRIGGER_THRESHOLD = 25        # 触发清理的文件数量阈值
PROTECTED_RECENT_COUNT = 3     # 最少保留最新 N 个

# 受保护的状态值（永不删除）
PROTECTED_SG_STATUS = {"exceeded", "failed", "in_progress"}


# ============================================================
# 工具函数
# ============================================================

def parse_timestamp(filename: str) -> Optional[datetime]:
    """从 checkpoint 文件名提取时间戳，失败返回 None"""
    match = re.search(r'(\d{8})_(\d{6})', filename)
    if not match:
        return None
    try:
        date_str, time_str = match.groups()
        return datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
    except ValueError:
        return None


def load_checkpoint(path: Path) -> Optional[dict]:
    """加载 checkpoint JSON 文件"""
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def is_protected(checkpoint_data: dict) -> bool:
    """
    判断 checkpoint 是否受保护（永不删除）。
    
    受保护条件（满足任一即保护）：
    1. R2 超限状态：sg_status 中任意值为 "exceeded"
    2. 任务失败/中断：sg_status 中任意值为 "failed" 或 "in_progress"
    3. 显式保护标记：metadata.protected = true
    """
    sg_status = checkpoint_data.get("sg_status", {})
    
    # 规则1：R2 超限状态
    if any(v == "exceeded" for v in sg_status.values()):
        return True
    
    # 规则2：任务失败/中断
    if any(v in PROTECTED_SG_STATUS for v in sg_status.values()):
        return True
    
    # 规则3：显式保护标记
    if checkpoint_data.get("metadata", {}).get("protected") is True:
        return True
    
    return False


def get_all_checkpoints(checkpoint_dir: Path) -> List[Dict]:
    """
    获取目录下所有 checkpoint 文件信息列表。
    
    Returns:
        List[Dict]，每个元素包含：
        path, filename, session_id, phase, iteration, 
        timestamp, sg_status, protected, mtime
    """
    if not checkpoint_dir.exists():
        return []
    
    checkpoints = []
    for f in sorted(checkpoint_dir.glob("checkpoint_*.json")):
        data = load_checkpoint(f)
        if data is None:
            continue
        
        ts = parse_timestamp(f.name)
        if ts is None:
            ts = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        
        checkpoints.append({
            "path": f,
            "filename": f.name,
            "session_id": data.get("session_id", "unknown"),
            "phase": data.get("phase", "unknown"),
            "iteration": data.get("iteration", 0),
            "timestamp": ts,
            "sg_status": data.get("sg_status", {}),
            "protected": is_protected(data),
            "mtime": f.stat().st_mtime
        })
    
    return checkpoints


# ============================================================
# 核心清理函数
# ============================================================

def cleanup_checkpoints(
    checkpoint_dir: str = None,
    dry_run: bool = False,
    force: bool = False,
    max_checkpoints: int = MAX_CHECKPOINTS,
    max_age_days: int = MAX_AGE_DAYS,
    protected_recent_count: int = PROTECTED_RECENT_COUNT,
    trigger_threshold: int = TRIGGER_THRESHOLD,
) -> Tuple[int, List[str]]:
    """
    清理 checkpoint 目录。
    
    清理规则（按优先级）：
    1. 受保护（protected=True）的 checkpoint 永不删除
    2. R2 超限 / 任务失败 / 任务中断 状态的 checkpoint 永不删除
    3. 按数量维度：保留最新 max_checkpoints 个
    4. 按时间维度：保留最近 max_age_days 天
    
    Args:
        checkpoint_dir: checkpoint 目录路径，默认 ~/.qclaw/skills/auditor/_checkpoints
        dry_run: True=只报告不删除
        force: True=忽略保护规则（危险！仅调试用）
        max_checkpoints: 最大保留数量
        max_age_days: 最大保留天数
        protected_recent_count: 最少保留最新 N 个
        trigger_threshold: 触发清理的文件数量阈值
    
    Returns:
        (removed_count, removed_files list)
    """
    if checkpoint_dir is None:
        checkpoint_dir = Path.home() / ".qclaw" / "skills" / "auditor" / "_checkpoints"
    else:
        checkpoint_dir = Path(checkpoint_dir)
    
    if not checkpoint_dir.exists():
        return 0, []
    
    checkpoints = get_all_checkpoints(checkpoint_dir)
    
    if len(checkpoints) <= max_checkpoints and not force:
        # 文件数未超限，检查是否有过期的
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        expired = [
            c for c in checkpoints
            if not c["protected"] and c["timestamp"].replace(tzinfo=timezone.utc) < cutoff
        ]
        if not expired:
            return 0, []
    
    # 按时间排序（最老的在前）
    sorted_cp = sorted(checkpoints, key=lambda x: x["timestamp"])
    
    # 分类：受保护 vs 可淘汰
    candidates = []   # 可淘汰
    protected = []   # 受保护
    
    for cp in sorted_cp:
        if cp["protected"]:
            protected.append(cp)
        else:
            candidates.append(cp)
    
    if not force:
        # 最少保留最新 N 个不受保护的（防止最新状态丢失）
        if len(candidates) > protected_recent_count:
            recent_unprotected = candidates[-protected_recent_count:]
            candidates = candidates[:-protected_recent_count]
            protected.extend(recent_unprotected)
    
    # 数量维度淘汰
    excess_count = len(checkpoints) - max_checkpoints
    to_delete_by_count = []
    if excess_count > 0 and len(candidates) >= excess_count:
        to_delete_by_count = candidates[:excess_count]
        candidates = candidates[excess_count:]
    
    # 时间维度淘汰
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    to_delete_by_age = [c for c in candidates if c["timestamp"].replace(tzinfo=timezone.utc) < cutoff]
    candidates = [c for c in candidates if c not in to_delete_by_age]
    
    # 合并删除列表（按时间，最老的先删）
    to_delete = sorted(to_delete_by_count + to_delete_by_age, key=lambda x: x["timestamp"])
    
    removed = []
    if dry_run:
        for cp in to_delete:
            removed.append(cp["filename"])
    else:
        for cp in to_delete:
            try:
                cp["path"].unlink()
                removed.append(cp["filename"])
            except Exception as e:
                print(f"删除失败 {cp['filename']}: {e}")
    
    return len(removed), removed


def get_checkpoint_stats(checkpoint_dir: str = None) -> Dict:
    """
    获取 checkpoint 目录统计信息。
    
    Returns:
        Dict 包含：
        - exists: bool，目录是否存在
        - total: int，总文件数
        - protected: int，受保护文件数
        - unprotected: int，可淘汰文件数
        - expired: int，已过期文件数
        - oldest: str，最老文件的 iso 时间戳
        - newest: str，最新文件的 iso 时间戳
        - cleanup_needed: bool，是否需要清理
        - thresholds: dict，当前阈值配置
    """
    if checkpoint_dir is None:
        checkpoint_dir = Path.home() / ".qclaw" / "skills" / "auditor" / "_checkpoints"
    else:
        checkpoint_dir = Path(checkpoint_dir)
    
    if not checkpoint_dir.exists():
        return {
            "exists": False,
            "total": 0,
            "protected": 0,
            "expired": 0,
            "oldest": None,
            "newest": None,
            "cleanup_needed": False,
            "message": "checkpoint 目录不存在"
        }
    
    checkpoints = get_all_checkpoints(checkpoint_dir)
    protected = [c for c in checkpoints if c["protected"]]
    unprotected = [c for c in checkpoints if not c["protected"]]
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    expired = [c for c in unprotected if c["timestamp"].replace(tzinfo=timezone.utc) < cutoff]
    
    return {
        "exists": True,
        "total": len(checkpoints),
        "protected": len(protected),
        "unprotected": len(unprotected),
        "expired": len(expired),
        "oldest": min(c["timestamp"] for c in checkpoints).isoformat() if checkpoints else None,
        "newest": max(c["timestamp"] for c in checkpoints).isoformat() if checkpoints else None,
        "cleanup_needed": len(checkpoints) > TRIGGER_THRESHOLD or len(expired) > 0,
        "thresholds": {
            "MAX_CHECKPOINTS": MAX_CHECKPOINTS,
            "MAX_AGE_DAYS": MAX_AGE_DAYS,
            "TRIGGER_THRESHOLD": TRIGGER_THRESHOLD,
            "PROTECTED_RECENT_COUNT": PROTECTED_RECENT_COUNT
        }
    }


# ============================================================
# CLI 入口
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Checkpoint 清理工具")
    parser.add_argument("--dir", default=None, help="checkpoint 目录路径")
    parser.add_argument("--dry-run", action="store_true", help="只报告不删除")
    parser.add_argument("--stats", action="store_true", help="只显示统计")
    parser.add_argument("--force", action="store_true", help="忽略保护规则（危险）")
    
    args = parser.parse_args()
    
    if args.stats:
        stats = get_checkpoint_stats(args.dir)
        print(json.dumps(stats, indent=2, default=str))
    else:
        removed_count, removed_files = cleanup_checkpoints(
            checkpoint_dir=args.dir,
            dry_run=args.dry_run,
            force=args.force
        )
        print(f"清理了 {removed_count} 个文件:")
        for f in removed_files:
            print(f"  - {f}")