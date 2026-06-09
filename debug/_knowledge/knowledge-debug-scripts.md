# 知识工程调试脚本
# 集成到 debug skill 的脚本工具中

## 概述

本模块提供 2 个 Python 调试脚本，用于验证知识文件增强是否成功插入，以及批量验证多个知识文件的增强结果。

---

## 脚本1：check_knowledge_insertion.py

验证知识文件增强是否成功插入到指定位置。

### 功能说明

- 读取目标文件，搜索指定章节标题
- 报告章节位置和文件总行数
- 验证插入后内容行数是否满足最小要求

### 完整代码

```python
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
```

### 使用示例

```bash
# 检查单个章节
python check_knowledge_insertion.py "C:\path\to\file.md" "量化策略"

# 检查章节并验证最小行数
python check_knowledge_insertion.py "C:\path\to\file.md" "量化策略" 100
```

### 输出示例

```
✅ 找到章节: 量化策略
   位置: 第156行
   文件总行数: 892
   插入后行数: 736
```

---

## 脚本2：batch_verify_knowledge.py

批量验证多个知识文件的增强结果。

### 功能说明

- 读取 JSON manifest 文件，批量检查多个知识文件
- 验证每个文件的行数、章节存在性
- 生成汇总报告

### Manifest 文件格式

```json
{
  "files": [
    {
      "path": "C:\\path\\to\\file1.md",
      "sections": ["章节1", "章节2"],
      "min_lines": 200
    },
    {
      "path": "C:\\path\\to\\file2.md",
      "sections": ["核心内容"],
      "min_lines": 100
    }
  ]
}
```

### 完整代码

```python
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
```

### 使用示例

```bash
# 创建示例 manifest
python batch_verify_knowledge.py --create-sample ./manifest.json

# 运行批量验证
python batch_verify_knowledge.py ./manifest.json
```

### 输出示例

```
============================================================
批量验证结果: 3个文件
============================================================
通过: 2/3

✅ C:\path\to\file1.md
   行数: 411 (期望>200)
   ✅ 调试命令
   ✅ 错误模式

❌ C:\path\to\file2.md
   行数: 45 (期望>100)
   ⚠️ 文件行数不足
   ✅ 健康检查

❌ C:\path\to\file3.md
   ⚠️ 文件不存在

============================================================
```

---

## 集成到 debug skill

这两个脚本可通过 debug skill 的 `script.sh` 调用：

```bash
# 知识插入验证
bash scripts/script.sh knowledge-check <文件路径> <章节标题> [最小行数]

# 知识库批量健康检查
bash scripts/script.sh knowledge-health <manifest.json>
```

---

## 依赖

- Python 3.6+
- 标准库：`sys`, `re`, `pathlib`, `json`

无需额外安装第三方库。