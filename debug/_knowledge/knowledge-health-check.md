# 知识库健康检查
# 集成到 debug skill 的 health 功能中

## 概述

本模块提供知识库文件的健康检查标准、处理流程和监控机制，确保知识文件满足质量要求并持续保持健康状态。

---

## 1. 知识库文件健康检查标准

### 1.1 检查项定义

| 检查项 | 健康标准 | 不健康信号 | 权重 |
|--------|---------|-----------|------|
| 文件大小 | 5KB~30KB | <3KB（内容不足）或>50KB（过于臃肿） | 高 |
| 章节数量 | 5~15章 | <3章（过简）或>20章（需拆分） | 高 |
| 公式数量 | 每章≥0个，全文件≥3个 | 全文件<2个公式（缺少量化内容） | 中 |
| 来源标注 | 每增强章节有来源标注 | 无来源标注或"来源未知" | 高 |
| 触发词 | 每文件≥3个触发词 | 无触发词（知识文件无法被调用） | 高 |
| 语言一致性 | 中文正文+英文变量+LaTeX公式 | 中英混排无规律 | 中 |
| 代码块 | 有示例代码或配置 | 纯文字无实践内容 | 低 |

### 1.2 健康评分计算

```python
def calculate_health_score(file_path):
    """计算知识文件健康评分（0-100）"""
    score = 100
    
    # 文件大小检查（-20分）
    size = Path(file_path).stat().st_size
    if size < 3072 or size > 51200:
        score -= 20
    
    # 章节数量检查（-15分）
    chapters = count_chapters(file_path)
    if chapters < 3 or chapters > 20:
        score -= 15
    
    # 公式数量检查（-10分）
    formulas = count_formulas(file_path)
    if formulas < 2:
        score -= 10
    
    # 来源标注检查（-20分）
    if not has_source_markers(file_path):
        score -= 20
    
    # 触发词检查（-15分）
    triggers = count_trigger_words(file_path)
    if triggers < 3:
        score -= 15
    
    # 语言一致性检查（-10分）
    if not is_language_consistent(file_path):
        score -= 10
    
    return max(0, score)

# 健康等级定义
HEALTH_EXCELLENT = range(90, 101)   # 90-100
HEALTH_GOOD = range(70, 90)         # 70-89
HEALTH_WARNING = range(50, 70)       # 50-69
HEALTH_CRITICAL = range(0, 50)      # 0-49
```

### 1.3 快速健康检查命令

```bash
# 快速检查文件大小和行数
wc -l <file> && ls -la <file>

# 检查章节数量
grep -c "^## " <file>

# 检查公式数量
grep -c '\$\$' <file>

# 检查触发词
grep -E "(触发词|关键词|适用场景)" <file> | wc -l
```

---

## 2. 39个知识文件健康检查结果

### 2.1 核心文件（评分≥85）

| 文件 | 状态 | 行数 | 增强章节数 | 说明 |
|------|------|------|-----------|------|
| criminal-compliance.md | ✅健康 | 411 | 8 | 最完善，FCPA+不起诉+DOJ罚款 |
| hk-stock-analysis.md | ✅健康 | 392 | 6 | 港股核心文件，PB+管线+做空 |
| alternative-data-guide.md | ✅健康 | 326 | 10 | 量化因子+信号衰减 |
| macro-forecasting-model.md | ✅健康 | 304 | 5 | 宏观框架完整 |
| content-director.md | ✅健康 | 267 | 6 | 平台算法完整 |
| stock-analyst.md | ✅健康 | 266 | 5 | 护城河+渗透率 |
| platform-adapter.md | ✅健康 | 227 | 5 | 算法评分完整 |

### 2.2 标准文件（评分70-84）

| 文件 | 状态 | 行数 | 增强章节数 | 说明 |
|------|------|------|-----------|------|
| risk-management.md | ✅健康 | 245 | 4 | 风险管理框架完整 |
| data-engineering.md | ✅健康 | 238 | 4 | 数据工程流程清晰 |
| factor-investing.md | ✅健康 | 221 | 4 | 多因子模型 |
| quantitative-fund.md | ✅健康 | 218 | 4 | 基金架构设计 |
| china-valuation.md | ✅健康 | 212 | 3 | A股估值方法 |
| financial-report.md | ✅健康 | 198 | 3 | 财务报表分析 |
| quantitative-trading.md | ✅健康 | 195 | 4 | 交易系统完整 |

### 2.3 需优化文件（评分50-69）

| 文件 | 状态 | 行数 | 增强章节数 | 说明 |
|------|------|------|-----------|------|
| alternative-investment.md | ⚠️需优化 | 156 | 2 | 章节偏少 |
| financial-derivatives.md | ⚠️需优化 | 142 | 2 | 公式不足 |
| investment-advisory.md | ⚠️需优化 | 138 | 2 | 触发词偏少 |
| ... | ... | ... | ... | ... |

### 2.4 重建建议文件（评分<50）

| 文件 | 状态 | 行数 | 说明 |
|------|------|------|------|
| test-file.md | ❌重建 | 23 | 内容严重不足 |
| placeholder.md | ❌重建 | 12 | 纯占位符 |
| ... | ... | ... | ... |

---

## 3. 知识库不健康处理流程

### 3.1 处理流程图

```
识别不健康文件
       │
       ▼
┌─────────────────┐
│ 步骤1: 识别问题  │
│ 行数<50或>500   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 步骤2: 分析根因  │
│ 章节完整性检查   │
│ 公式/表格检查    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 步骤3: 判定处理  │
│ 可修复 → 修复    │
│ 不可修复 → 重建  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 步骤4: 验证通过  │
│ 重新健康检查     │
└─────────────────┘
```

### 3.2 详细步骤说明

#### 步骤1：识别不健康文件

```python
def identify_unhealthy_files(directory, threshold_min=50, threshold_max=500):
    """识别不健康文件
    
    参数:
        directory: 知识库目录
        threshold_min: 行数下限
        threshold_max: 行数上限
    
    返回:
        list: 不健康文件列表
    """
    unhealthy = []
    
    for md_file in Path(directory).glob("**/*.md"):
        lines = len(md_file.read_text(encoding='utf-8').split('\n'))
        
        if lines < threshold_min:
            unhealthy.append({
                'file': str(md_file),
                'reason': f'内容不足({lines}行 < {threshold_min})',
                'severity': 'high'
            })
        elif lines > threshold_max:
            unhealthy.append({
                'file': str(md_file),
                'reason': f'内容臃肿({lines}行 > {threshold_max})',
                'severity': 'medium'
            })
    
    return unhealthy
```

#### 步骤2：检查章节完整性

```bash
# 统计章节数量
grep "^## " <file> | wc -l

# 显示章节列表
grep "^## " <file>

# 检查是否有增强章节
grep "^### " <file> | head -20
```

#### 步骤3：验证增强内容有效性

```bash
# 检查公式数量
grep -c '\$\$' <file>

# 检查表格数量
grep -c '^|' <file>

# 检查来源标注
grep -E "(来源:|参考:|依据:)" <file>

# 检查触发词
grep -E "(适用场景|触发词|使用条件)" <file>
```

#### 步骤4：修复或重建决策

| 情况 | 决策 | 处理方式 |
|------|------|---------|
| 行数不足+章节完整 | 修复 | 补充内容/合并章节 |
| 行数不足+章节缺失 | 重建 | 重新编写完整内容 |
| 行数臃肿+结构清晰 | 修复 | 拆分大章节 |
| 行数臃肿+结构混乱 | 重建 | 重构内容结构 |
| 格式严重损坏 | 重建 | 使用模板重新生成 |

---

## 4. 知识库健康监控Cron

### 4.1 监控任务配置

```yaml
# openclaw cron 配置
cron:
  knowledge-health-check:
    schedule: "0 9 * * 1"  # 每周一 09:00
    command: python scripts/batch_verify_knowledge.py /path/to/manifest.json
    timeout: 300
    retry: 3
    alert:
      on_failure: true
      channels: [email, webhook]
```

### 4.2 异常告警规则

| 告警级别 | 条件 | 处理 |
|---------|------|------|
| P1-紧急 | 文件行数变化>±30% | 立即触发审计 |
| P2-警告 | 健康评分下降>20 | 24h内检查 |
| P3-提醒 | 新增文件未检查 | 3天内补检 |

### 4.3 健康报告模板

```markdown
# 知识库健康报告

## 概览
- 检查时间: {timestamp}
- 文件总数: {total}
- 健康文件: {healthy}
- 需优化: {warning}
- 严重问题: {critical}

## P1问题（紧急处理）
{files}

## P2问题（需关注）
{files}

## 趋势分析
- 本周健康率: {rate}%
- 与上周对比: {trend}
```

### 4.4 自动修复建议

当检测到不健康文件时，自动生成修复建议：

```python
def generate_fix_suggestions(file_path, issues):
    """生成修复建议
    
    参数:
        file_path: 文件路径
        issues: 问题列表
    
    返回:
        str: 修复建议文本
    """
    suggestions = []
    
    for issue in issues:
        if issue['type'] == 'insufficient_lines':
            suggestions.append(
                f"建议补充{(50 - issue['current_lines'])}行内容，"
                "可在现有章节中增加示例、表格或公式"
            )
        elif issue['type'] == 'missing_sources':
            suggestions.append(
                "建议为每个增强章节添加来源标注，"
                "格式: > 来源: [来源名称](链接)"
            )
        elif issue['type'] == 'few_triggers':
            suggestions.append(
                "建议在文件末尾添加触发词章节，"
                "包含至少5个触发场景关键词"
            )
    
    return "\n".join(suggestions)
```

---

## 5. 健康检查集成命令

### 5.1 debug skill 增强命令

```bash
# 单文件健康检查
debug health check <file_path>

# 批量健康检查
debug health batch <manifest.json>

# 生成健康报告
debug health report --output ./health_report.md

# 自动修复
debug health fix <file_path> --dry-run
```

### 5.2 健康评分API

```python
# 健康检查函数
def health_check(file_path):
    """返回 (score, issues)"""
    score = calculate_health_score(file_path)
    issues = []
    
    if score < 50:
        issues.append({'level': 'critical', 'msg': '健康评分过低'})
    elif score < 70:
        issues.append({'level': 'warning', 'msg': '需优化'})
    
    return score, issues
```

---

## 6. 健康标准参考表

### 6.1 文件大小参考

| 类型 | 推荐大小 | 最小 | 最大 |
|------|---------|------|------|
| 核心技能文件 | 15KB~30KB | 10KB | 50KB |
| 普通技能文件 | 8KB~20KB | 5KB | 40KB |
| 工具脚本 | 3KB~10KB | 1KB | 20KB |
| 配置文件 | 1KB~5KB | 0.5KB | 10KB |

### 6.2 章节结构参考

| 文件类型 | 章节数 | 每章行数 | 总行数 |
|---------|-------|---------|-------|
| 完整技能 | 8~12章 | 20~50行 | 200~500行 |
| 简要技能 | 3~5章 | 30~60行 | 100~250行 |
| 工具脚本 | 2~4章 | 40~80行 | 80~250行 |

---

## 附录：健康检查脚本

### A. 快速检查脚本

```bash
#!/bin/bash
# quick_health_check.sh - 快速健康检查

FILE=$1
echo "=== 健康检查: $FILE ==="
echo "行数: $(wc -l < "$FILE")"
echo "章节数: $(grep -c "^## " "$FILE")"
echo "公式数: $(grep -c '\$\$' "$FILE")"
echo "触发词: $(grep -cE "(触发词|适用场景)" "$FILE")"
echo "来源标注: $(grep -cE "(来源:|参考:)" "$FILE")"
```

### B. 完整检查脚本

```python
#!/usr/bin/env python3
"""知识文件完整健康检查"""

import sys
from pathlib import Path

def full_health_check(file_path):
    """执行完整健康检查"""
    content = Path(file_path).read_text(encoding='utf-8')
    lines = content.split('\n')
    
    results = {
        'lines': len(lines),
        'chapters': len([l for l in lines if l.strip().startswith('## ')]),
        'formulas': content.count('$$') + content.count('$'),
        'triggers': len([l for l in lines if '触发词' in l or '适用场景' in l]),
        'sources': len([l for l in lines if '来源:' in l or '参考:' in l]),
        'size': Path(file_path).stat().st_size
    }
    
    print(f"\n{'='*50}")
    print(f"健康检查: {file_path}")
    print(f"{'='*50}")
    print(f"行数: {results['lines']}")
    print(f"章节: {results['chapters']}")
    print(f"公式: {results['formulas']}")
    print(f"触发词: {results['triggers']}")
    print(f"来源标注: {results['sources']}")
    print(f"文件大小: {results['size']/1024:.1f}KB")
    print(f"{'='*50}")
    
    return results

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python full_health_check.py <file>")
        sys.exit(1)
    full_health_check(sys.argv[1])
```