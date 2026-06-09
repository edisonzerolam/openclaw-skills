"""knowledge_cache.py — 知识文件内存缓存

auditor 的知识文件在 _knowledge/ 目录下，每次触发都重新读取磁盘。
本模块提供基于文件修改时间的内存缓存，减少 I/O。

使用方式：
    from knowledge_cache import knowledge_cache, load_knowledge_cached
    
    # 加载知识文件（带缓存）
    content = load_knowledge_cached("core-principles/audit-process.md")
    
    # 清除缓存
    knowledge_cache.clear()
"""

import os
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """缓存条目"""
    mtime: float  # 文件修改时间
    size: int      # 文件大小
    content: str   # 文件内容


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
    
    def get(self, relative_path: str) -> Optional[str]:
        """
        获取知识文件内容（缓存优先）。
        
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
                
                # 文件未修改，使用缓存
                if entry.mtime == current_mtime and entry.size == current_size:
                    self._hits += 1
                    return entry.content
            
            # 缓存未命中或文件已修改，重新读取
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self._cache[relative_path] = CacheEntry(
                mtime=current_mtime,
                size=current_size,
                content=content
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
        content = load_knowledge_cached("core-principles/audit-process.md")
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
    content = load_knowledge_cached("core-principles/audit-principles.md")
    print("First load:", "ok" if content else "not found")
    print("Stats:", knowledge_cache_stats())
    
    # 第二次加载（缓存命中）
    content = load_knowledge_cached("core-principles/audit-principles.md")
    print("Second load:", "ok" if content else "not found")
    print("Stats:", knowledge_cache_stats())