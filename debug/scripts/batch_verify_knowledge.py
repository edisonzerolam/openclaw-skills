#!/usr/bin/env python3
"""批量验证知识文件增强结果"""

import json
import sys
from pathlib import Path

def batch_verify(manifest_path):
    """批量验证知识增强结果
    
    参数:
        manifest_path: JSON manifest 文件路径
    
    返回:
        bool: 是否全部通过
    """
    # 读取 manifest
    try:
        manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    except FileNotFoundError:
        print(f"❌ Manifest 文件不存在: {manifest_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Manifest JSON 解析失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 读取 Manifest 失败: {e}")
        return False
    
    results = []
    
    for item in manifest['files']:
        file_path = item['path']
        expected_sections = item.get('sections', [])
        expected_lines = item.get('min_lines', 0)
        
        # 读取文件
        if Path(file_path).exists():
            content = Path(file_path).read_text(encoding='utf-8')
        else:
            content = ""
        
        lines = content.split('\n')
        
        # 检查每个章节
        section_results = []
        for section in expected_sections:
            found = any(section in line for line in lines)
            section_results.append({'section': section, 'found': found})
        
        results.append({
            'file': file_path,
            'total_lines': len(lines),
            'expected_min': expected_lines,
            'line_ok': len(lines) >= expected_lines,
            'sections': section_results,
            'file_exists': Path(file_path).exists()
        })
    
    # 打印汇总
    print(f"\n{'='*60}")
    print(f"批量验证结果: {len(results)}个文件")
    print(f"{'='*60}")
    
    ok_count = sum(
        1 for r in results 
        if r['file_exists'] and r['line_ok'] and all(s['found'] for s in r['sections'])
    )
    
    print(f"通过: {ok_count}/{len(results)}")
    
    for r in results:
        if not r['file_exists']:
            status = "❌(不存在)"
        elif r['line_ok'] and all(s['found'] for s in r['sections']):
            status = "✅"
        else:
            status = "❌"
        
        print(f"\n{status} {r['file']}")
        print(f"   行数: {r['total_lines']} (期望>{r['expected_min']})")
        
        if not r['file_exists']:
            print(f"   ⚠️ 文件不存在")
            continue
        
        for s in r['sections']:
            mark = "✅" if s['found'] else "❌"
            print(f"   {mark} {s['section']}")
    
    print(f"\n{'='*60}")
    
    return ok_count == len(results)


def create_sample_manifest(output_path):
    """创建示例 manifest 文件"""
    sample = {
        "files": [
            {
                "path": "/home/user\\.qclaw\\skills\\debug\\test1.md",
                "sections": ["调试命令", "错误模式"],
                "min_lines": 100
            },
            {
                "path": "/home/user\\.qclaw\\skills\\debug\\test2.md",
                "sections": ["健康检查"],
                "min_lines": 50
            }
        ]
    }
    
    Path(output_path).write_text(json.dumps(sample, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"示例 manifest 已创建: {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python batch_verify_knowledge.py <manifest.json>")
        print("")
        print("示例:")
        print("  python batch_verify_knowledge.py ./manifest.json")
        print("")
        print("创建示例 manifest:")
        print("  python batch_verify_knowledge.py --create-sample ./sample.json")
        sys.exit(1)
    
    if sys.argv[1] == '--create-sample':
        create_sample_manifest(sys.argv[2] if len(sys.argv) > 2 else 'sample_manifest.json')
        sys.exit(0)
    
    manifest_path = sys.argv[1]
    success = batch_verify(manifest_path)
    sys.exit(0 if success else 1)