"""knowledge_cache.py — 知识文件内存缓存（v3.4 分层TTL）

agent-planner 的知识文件在 _knowledge/ 目录下，每次触发都重新读取磁盘。
本模块提供基于文件修改时间+TTL的内存缓存，减少 I/O。

v3.4 新增分层 TTL：
- 高频变动文件（LEARNINGS.md）= 10min
- 低频文件（pitfall-library/plan-template）= 24h
- 全局默认 = 60min

使用方式：
    from knowledge_cache import knowledge_cache, load_knowledge_cached
    
    # 加载知识文件（带缓存）
    content = load_knowledge_cached("core-principles/planning-patterns.md")
    
    # 清除缓存
    knowledge_cache.clear()
"""

import os
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field


# 分层 TTL 配置（秒）
TIERED_TTL = {
    # 高频变动文件
    "_refined/LEARNINGS.md": 10 * 60,           # 10 分钟
    # 低频变动文件
    "_enhancement/pitfall-library.md": 24 * 3600,  # 24 小时
    "_enhancement/plan-template.md": 24 * 3600,    # 24 小时
    "_enhancement/spawn-patterns.md": 24 * 3600,   # 24 小时
    "_enhancement/workspace-zones.md": 24 * 3600,  # 24 小时
    "_enhancement/knowledge-base-integration.md": 24 * 3600,  # 24 小时
}
DEFAULT_TTL = 60 * 60  # 全局默认 60 分钟


@dataclass
class CacheEntry:
    """缓存条目"""
    mtime: float  # 文件修改时间
    size: int      # 文件大小
    content: str   # 文件内容
    cached_at: float = field(default_factory=time.time)  # 缓存时间
    ttl: int = DEFAULT_TTL  # TTL（秒）


class KnowledgeCache:
    """知识文件缓存器"""
    
    def __init__(self, knowledge_root: Optional[str] = None):
        """
        Args:
            knowledge_root: 知识库根目录，默认从环境变量或相对位置推断
        """
        if knowledge_root:
            self.knowledge_root = Path(knowledge_root)
        else:
            # 推断：与本文件同级的 _knowledge/
            self.knowledge_root = Path(__file__).parent.parent / "_knowledge"
        
        self._cache: Dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0
    
    def _get_path(self, relative_path: str) -> Path:
        """获取完整路径"""
        return self.knowledge_root / relative_path
    
    def _get_ttl(self, relative_path: str) -> int:
        """获取文件的 TTL（秒）"""
        for pattern, ttl in TIERED_TTL.items():
            if pattern in relative_path:
                return ttl
        return DEFAULT_TTL
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """检查缓存是否过期"""
        return (time.time() - entry.cached_at) > entry.ttl
    
    def get(self, relative_path: str) -> Optional[str]:
        """
        获取知识文件内容（缓存优先，TTL过期自动失效）。
        
        Args:
            relative_path: 相对于知识库根目录的路径
            
        Returns:
            文件内容，或 None（文件不存在）
        """
        path = self._get_path(relative_path)
        
        if not path.exists():
            return None
        
        try:
            current_mtime = path.stat().st_mtime
            current_size = path.stat().st_size
            
            # 检查缓存
            if relative_path in self._cache:
                entry = self._cache[relative_path]
                
                # 检查是否过期
                if self._is_expired(entry):
                    del self._cache[relative_path]
                # 文件未修改且未过期，使用缓存
                elif entry.mtime == current_mtime and entry.size == current_size:
                    self._hits += 1
                    return entry.content
            
            # 缓存未命中/过期/文件已修改，重新读取
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self._cache[relative_path] = CacheEntry(
                mtime=current_mtime,
                size=current_size,
                content=content,
                cached_at=time.time(),
                ttl=self._get_ttl(relative_path)
            )
            self._misses += 1
            
            return content
            
        except Exception:
            return None
    
    def invalidate(self, relative_path: str):
        """使指定文件的缓存失效"""
        if relative_path in self._cache:
            del self._cache[relative_path]
    
    def clear(self):
        """清除所有缓存"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def stats(self) -> Dict:
        """获取缓存统计"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total": total,
            "hit_rate_percent": round(hit_rate, 1),
            "cached_files": len(self._cache)
        }


# 全局缓存实例
knowledge_cache = KnowledgeCache()


def load_knowledge_cached(relative_path: str) -> Optional[str]:
    """
    加载知识文件（使用全局缓存）。
    
    这是最常用的接口：
        content = load_knowledge_cached("core-principles/planning-patterns.md")
    """
    return knowledge_cache.get(relative_path)


def clear_knowledge_cache():
    """清除全局缓存"""
    knowledge_cache.clear()


def knowledge_cache_stats() -> Dict:
    """获取全局缓存统计"""
    return knowledge_cache.stats()


# 示例用法
if __name__ == "__main__":
    # 测试缓存
    print("Knowledge root:", knowledge_cache.knowledge_root)
    
    # 首次加载（缓存未命中）
    content = load_knowledge_cached("core-principles/planning-principles.md")
    print("First load:", "ok" if content else "not found")
    print("Stats:", knowledge_cache_stats())
    
    # 第二次加载（缓存命中）
    content = load_knowledge_cached("core-principles/planning-principles.md")
    print("Second load:", "ok" if content else "not found")
    print("Stats:", knowledge_cache_stats())