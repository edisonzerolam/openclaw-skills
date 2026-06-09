# S3c Review-Loop Protocol — Checkpoint Cleanup Strategy

> 版本：v1.0 | 状态：draft | 依赖：auditor v6.4+  
> 解决：P2-1 风险 — `_checkpoints/` 目录无限增长

---

## C1. 风险定义

| 风险ID | 描述 | 影响 |
|--------|------|------|
| P2-1 | `_checkpoints/` 目录无限增长，无清理策略 | 磁盘耗尽 + 文件混乱 |

**现状**：
- 路径：`~/.qclaw/skills/auditor/_checkpoints/`
- 格式：JSON（session_id + phase + iteration + timestamp + queue + sg_status）
- 写入时机：S3c.4 后 + 全部超时 + sessions_yield 前

---

## C2. Checkpoint 文件格式规范

每个 checkpoint 文件名格式：
```
checkpoint_{session_id}_{phase}_{iteration}_{timestamp}.json
```

示例：
```
checkpoint_session-abc123_S3c_004_20260530_011500.json
checkpoint_session-def456_S4_002_20260530_012300.json
```

JSON 内容：
```json
{
  "session_id": "session-abc123",
  "phase": "S3c",
  "iteration": 4,
  "timestamp": "2026-05-30T01:15:00+08:00",
  "queue": ["task1", "task2", "task3"],
  "sg_status": {
    "S1": "pass",
    "S2": "pass",
    "S3c": "pending",
    "S4": "pending"
  },
  "metadata": {
    "created_by": "auditor",
    "version": "6.4",
    "protected": false
  }
}
```

---

## C3. 保留策略（Retention Policy）

### C3.1 双维度保留规则

| 维度 | 阈值 | 说明 |
|------|------|------|
| **数量维度** | 最近 **20 个** checkpoint 文件 | 保留最新 20 个，无论时间 |
| **时间维度** | 最近 **7 天** | 保留 7 天内的，无论数量 |

**淘汰顺序**（先到先删）：
1. 超出数量上限 → 删除最旧的
2. 超出时间上限 → 删除最旧的
3. 淘汰前检查保护规则（C5）

### C3.2 保留阈值计算

```
有效 checkpoint = (数量 ≤ 20) AND (年龄 ≤ 7天)

超出任意条件 → 进入淘汰候选池
```

### C3.3 特殊状态保护（不受数量/时间限制）

以下状态的 checkpoint **永不删除**：
- `sg_status` 中任意 phase = `"exceeded"`（R2 超限）
- `metadata.protected = true`（显式保护标记）
- 关联的审计任务状态为 `failed` 或 `in_progress`

---

## C4. 清理时机（Cleanup Trigger Points）

### C4.1 主动清理点（推荐）

| 清理点 | 时机 | 说明 |
|--------|------|------|
| **S5.10 后** | 审计任务正常完成归档后 | 清理旧的非保护 checkpoint |
| **S2 开始前** | 新审计任务启动时 | 清理过期的（>7天）旧 checkpoint |
| **auditor skill 初始化时** | SKILL.md 加载完成后 | 懒清理（lazy cleanup） |

### C4.2 被动清理策略

每次写入 checkpoint 前，检查是否需要触发清理：
- 文件数 > 25 → 触发清理（保留最近 20 个）
- 无需每次写入都清理，避免 I/O 开销

### C4.3 清理执行入口

```
auditor skill 初始化
    ↓
执行 cleanup_checkpoints()（懒清理）
    ↓
返回 (需要清理数量, 清理后剩余数量)
    ↓
条件满足（>25 或 初始化时）→ 执行清理
```

---

## C5. 保护规则（Protection Rules）

### C5.1 必须保留的 Checkpoint

以下条件的 checkpoint **永不删除**：

| 保护条件 | 检测方式 | 说明 |
|---------|---------|------|
| **R2 超限状态** | `sg_status.* = "exceeded"` | 用于主会话决策 |
| **任务失败/中断** | `sg_status.* = "failed"` 或 `"in_progress"` | 用于恢复参考 |
| **显式保护标记** | `metadata.protected = true` | 临时保护 |
| **最新 checkpoint** | 排序后最年轻的 3 个 | 防止最新状态丢失 |

### C5.2 删除前验证（Deletion Guard）

```python
def can_delete(checkpoint_path: Path) -> bool:
    """
    删除前验证：任何保护条件触发 → 禁止删除
    """
    data = json.loads(checkpoint_path.read_text(encoding='utf-8'))
    
    # 规则1：R2 超限状态
    if any(v == "exceeded" for v in data.get("sg_status", {}).values()):
        return False
    
    # 规则2：任务失败/中断
    if any(v in ("failed", "in_progress") for v in data.get("sg_status", {}).values()):
        return False
    
    # 规则3：显式保护
    if data.get("metadata", {}).get("protected") is True:
        return False
    
    return True
```

### C5.3 受保护场景示例

```
✅ 可以删除：
checkpoint_session-abc_S3c_001_20260520.json  (sg_status 全 pass，7天前)
checkpoint_session-def_S4_003_20260525.json  (sg_status 全 pass，旧文件)

❌ 禁止删除：
checkpoint_session-xyz_S3c_005_20260528.json  (sg_status.S3c = "exceeded")
checkpoint_session-uvw_S4_002_20260527.json  (sg_status.S4 = "in_progress")
checkpoint_session-rst_S5_001_20260529.json  (metadata.protected = true)
```

---

## C6. 清理阈值（Cleanup Thresholds）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `MAX_CHECKPOINTS` | 20 | 最大保留数量（时间维度触发前先触发的数量） |
| `MAX_AGE_DAYS` | 7 | 最大保留天数 |
| `TRIGGER_THRESHOLD` | 25 | 触发清理的文件数量阈值 |
| `PROTECTED_RECENT_COUNT` | 3 | 最少保留最新 N 个（即使超过数量限制） |

**阈值行为说明**：
- 文件数 1-20：正常保留
- 文件数 21-25：触发懒清理警告，但不阻塞写入
- 文件数 > 25：强制执行清理，删除最旧的直到 ≤ 20
- 超过 7 天的文件：独立时间维度清理

---

## C7. 实现代码（Python）

### C7.1 cleanup_checkpoints.py（清理脚本）

```python
"""
cleanup_checkpoints.py — Checkpoint 清理模块

auditor v6.4+ 内置，作为 checkpoint 生命周期管理的一部分。

使用方式：
    from cleanup_checkpoints import cleanup_checkpoints, get_checkpoint_stats
    
    # 清理（保留最近 20 个 + 7 天内）
    removed = cleanup_checkpoints(checkpoint_dir="~/.qclaw/skills/auditor/_checkpoints")
    print(f"清理了 {removed} 个 checkpoint 文件")
    
    # 查看统计
    stats = get_checkpoint_stats(checkpoint_dir)
    print(stats)
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple, Optional

# 清理阈值
MAX_CHECKPOINTS = 20          # 最大保留数量
MAX_AGE_DAYS = 7              # 最大保留天数
TRIGGER_THRESHOLD = 25        # 触发清理的文件数量阈值
PROTECTED_RECENT_COUNT = 3     # 最少保留最新 N 个

# 受保护的状态值
PROTECTED_SG_STATUS = {"exceeded", "failed", "in_progress"}


def parse_timestamp(filename: str) -> Optional[datetime]:
    """从 checkpoint 文件名提取时间戳"""
    import re
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
    """判断 checkpoint 是否受保护（永不删除）"""
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
    """获取目录下所有 checkpoint 文件信息"""
    if not checkpoint_dir.exists():
        return []
    
    checkpoints = []
    for f in checkpoint_dir.glob("checkpoint_*.json"):
        data = load_checkpoint(f)
        if data is None:
            continue
        
        ts = parse_timestamp(f.name)
        if ts is None:
            ts = datetime.fromtimestamp(f.stat().st_mtime)
        
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


def cleanup_checkpoints(
    checkpoint_dir: str = None,
    dry_run: bool = False,
    force: bool = False
) -> Tuple[int, List[str]]:
    """
    清理 checkpoint 目录。
    
    Args:
        checkpoint_dir: checkpoint 目录路径
        dry_run: True=只报告不删除
        force: True=忽略保护规则（危险！仅调试用）
    
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
    
    if len(checkpoints) <= MAX_CHECKPOINTS:
        # 文件数未超限，检查是否有过期的
        cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
        expired = [
            c for c in checkpoints
            if not c["protected"] and c["timestamp"].replace(tzinfo=timezone.utc) < cutoff
        ]
        if not expired:
            return 0, []
    
    # 按时间排序（最老的在前）
    sorted_cp = sorted(checkpoints, key=lambda x: x["timestamp"])
    
    # 确定保留的候选
    candidates = []
    protected = []
    
    for cp in sorted_cp:
        if cp["protected"]:
            protected.append(cp)  # 受保护的不进入淘汰池
        else:
            candidates.append(cp)
    
    # 最少保留最新 PROTECTED_RECENT_COUNT 个（即使不在保护列表中）
    recent_unprotected = [c for c in candidates[-PROTECTED_RECENT_COUNT:] if not c["protected"]]
    protected.extend(recent_unprotected)
    candidates = candidates[:-PROTECTED_RECENT_COUNT] if len(candidates) > PROTECTED_RECENT_COUNT else []
    
    # 数量维度：超过 MAX_CHECKPOINTS 的部分标记为可删除
    excess_count = len(checkpoints) - MAX_CHECKPOINTS
    to_delete_by_count = []
    if excess_count > 0 and len(candidates) >= excess_count:
        to_delete_by_count = candidates[:excess_count]
        candidates = candidates[excess_count:]
    
    # 时间维度：超过 MAX_AGE_DAYS 的部分标记为可删除
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    to_delete_by_age = [c for c in candidates if c["timestamp"].replace(tzinfo=timezone.utc) < cutoff]
    candidates = [c for c in candidates if c not in to_delete_by_age]
    
    # 合并删除列表
    to_delete = to_delete_by_count + to_delete_by_age
    to_delete = sorted(to_delete, key=lambda x: x["timestamp"])  # 按时间，最老的先删
    
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
    """获取 checkpoint 目录统计信息"""
    if checkpoint_dir is None:
        checkpoint_dir = Path.home() / ".qclaw" / "skills" / "auditor" / "_checkpoints"
    else:
        checkpoint_dir = Path(checkpoint_dir)
    
    if not checkpoint_dir.exists():
        return {
            "exists": False,
            "total": 0,
            "protected": 0,
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
            "TRIGGER_THRESHOLD": TRIGGER_THRESHOLD
        }
    }


# CLI 入口
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
```

### C7.2 使用示例

```python
from cleanup_checkpoints import cleanup_checkpoints, get_checkpoint_stats

# 1. 查看统计（不清理）
stats = get_checkpoint_stats()
print(f"总计: {stats['total']} | 受保护: {stats['protected']} | 过期: {stats['expired']}")
print(f"需要清理: {stats['cleanup_needed']}")

# 2. 试运行（dry-run）
removed_count, removed_files = cleanup_checkpoints(dry_run=True)
print(f"将清理 {removed_count} 个文件")

# 3. 正式清理
removed_count, removed_files = cleanup_checkpoints()
print(f"已清理 {removed_count} 个文件")
```

### C7.3 集成到 auditor SKILL.md

在 Phase-S 的 S5.10 后追加清理调用：

```python
# S5.10 经验写入后
# → 触发 checkpoint 懒清理
from cleanup_checkpoints import cleanup_checkpoints

removed_count, removed_files = cleanup_checkpoints()
if removed_count > 0:
    print(f"[S5.10] checkpoint 清理：{removed_count} 个旧文件已清理")
```

---

## C8. 批量清理脚本（PowerShell）

适用于 Windows 手动执行：

```powershell
# cleanup-checkpoints.ps1
# 用法：.\cleanup-checkpoints.ps1 [-DryRun] [-Force]

param(
    [switch]$DryRun,
    [switch]$Force
)

$checkpointDir = Join-Path $HOME ".qclaw\skills\auditor\_checkpoints"
$MAX_AGE_DAYS = 7
$MAX_CHECKPOINTS = 20

if (-Not (Test-Path $checkpointDir)) {
    Write-Host "目录不存在：$checkpointDir" -ForegroundColor Yellow
    exit 0
}

Write-Host "=== Checkpoint 清理工具 ===" -ForegroundColor Cyan
Write-Host "目录：$checkpointDir"
Write-Host "最大保留：$MAX_CHECKPOINTS 个 或 $MAX_AGE_DAYS 天"
Write-Host ""

$files = Get-ChildItem "$checkpointDir\checkpoint_*.json" | Sort-Object LastWriteTime

Write-Host "当前文件数：$($files.Count)"
Write-Host ""

if ($DryRun) {
    Write-Host "【试运行模式】以下文件将被删除：" -ForegroundColor Yellow
}

$cutoffDate = (Get-Date).AddDays(-$MAX_AGE_DAYS)
$removed = 0

foreach ($file in $files) {
    $shouldRemove = $false
    
    # 数量维度检查（超过20个，删除最旧的）
    $fileIndex = $files.IndexOf($file)
    if ($files.Count -gt $MAX_CHECKPOINTS -and $fileIndex -lt ($files.Count - $MAX_CHECKPOINTS)) {
        $shouldRemove = $true
    }
    
    # 时间维度检查
    if ($file.LastWriteTime -lt $cutoffDate) {
        $shouldRemove = $true
    }
    
    if ($shouldRemove) {
        if ($DryRun) {
            Write-Host "  [将删除] $($file.Name)" -ForegroundColor Yellow
        } else {
            Remove-Item $file.FullName -Force
            Write-Host "  [已删除] $($file.Name)" -ForegroundColor Green
        }
        $removed++
    }
}

Write-Host ""
Write-Host "处理结果：删除了 $removed 个文件" -ForegroundColor $(if ($removed -gt 0) { "Green" } else { "White" })
```

---

## C9. 监控与告警

### C9.1 告警阈值

| 指标 | 警告阈值 | 阻塞阈值 | 处理动作 |
|------|---------|---------|---------|
| checkpoint 文件数 | > 20 | > 50 | 写入前阻塞，强制清理 |
| 单个文件大小 | > 100KB | > 500KB | 检查内容，告警 |
| 过期文件比例 | > 30% | > 60% | 批量清理 |

### C9.2 日志记录

每次清理操作记录到审计日志：

```
[S5.10] checkpoint 清理 | 2026-05-30 01:15 | 清理了 5 个旧文件 | 剩余 18 个
[S5.10] checkpoint 清理 | 2026-05-30 02:30 | 清理了 0 个（无需清理）| 剩余 18 个
```

---

## C10. 更新记录

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.0 | 2026-05-30 | 初始版本 |

---

## 附录：与其他增强层的接口

| 增强层 | 接口点 | 说明 |
|--------|--------|------|
| S5.9（进化引擎）| 清理后更新 LEARNINGS.md | 记录清理统计 |
| S3b（Merge Gate）| 清理前检查 | 确保归档完整性 |
| 超时恢复（B层） | 恢复后清理 | 恢复完成后清理临时 checkpoint |