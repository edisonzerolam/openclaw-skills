#!/usr/bin/env python3
"""检查知识文件增强插入结果"""

import sys
import re
from pathlib import Path

def check_insertion(file_path, section_title, min_lines_after=None):
    """检查章节是否成功插入
    
    参数:
        file_path: 文件路径
        section_title: 要搜索的章节标题
        min_lines_after: 可选，最小插入后行数
    
    返回:
        bool: 是否找到章节
    """
    # 读取文件
    try:
        content = Path(file_path).read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        return False
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False
    
    lines = content.split('\n')
    
    # 搜索章节标题（支持 Markdown 标题格式）
    pattern = rf'^\s*##\s*{re.escape(section_title)}'
    found_lines = [i+1 for i, line in enumerate(lines) if re.match(pattern, line)]
    
    # 报告结果
    if found_lines:
        print(f"✅ 找到章节: {section_title}")
        print(f"   位置: 第{found_lines[0]}行")
        print(f"   文件总行数: {len(lines)}")
        
        if min_lines_after:
            # 计算从插入点到文件末尾的行数
            insertion_point = found_lines[0]
            lines_after = len(lines) - insertion_point
            print(f"   插入后行数: {lines_after}")
            if lines_after < min_lines_after:
                print(f"⚠️  警告: 插入后内容行数({lines_after})少于预期({min_lines_after})")
                return False
        return True
    else:
        print(f"❌ 未找到章节: {section_title}")
        print(f"   文件路径: {file_path}")
        print(f"   文件总行数: {len(lines)}")
        
        # 尝试模糊匹配，显示相似章节
        similar = [line.strip() for line in lines if section_title.lower() in line.lower() and line.strip().startswith('##')]
        if similar:
            print(f"   相似章节:")
            for s in similar[:5]:
                print(f"     - {s}")
        
        return False


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python check_knowledge_insertion.py <文件路径> <章节标题> [最小行数]")
        print("")
        print("示例:")
        print("  python check_knowledge_insertion.py ./test.md '量化策略'")
        print("  python check_knowledge_insertion.py ./test.md '量化策略' 100")
        sys.exit(1)
    
    file_path = sys.argv[1]
    section_title = sys.argv[2]
    min_lines_after = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    success = check_insertion(file_path, section_title, min_lines_after)
    sys.exit(0 if success else 1)