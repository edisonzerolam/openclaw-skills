# 增强层C：多语言内容处理

> 本增强层基于 ClawTeam 知识库增强实战中处理中文+英文+LaTeX混排内容的经验沉淀，用于指导 auditor 在审计多语言混排内容时的标准化规则。

---

## C1. 中文内容写入规则（强制）

### C1.1 Windows环境编码规范

```
中文内容写入规则（Windows环境）：

编码选择：
- Windows默认编码：GBK/GB2312（系统级）
- UTF-8 with BOM：微软推荐的中文文件编码
- UTF-8 without BOM：跨平台兼容但Windows下可能乱码

规则：
1. 含中文的文本文件 → 必须使用 UTF-8 with BOM
2. 含中文的CSV文件 → 必须使用 UTF-8 with BOM（Excel兼容性）
3. 纯英文文本文件 → 可使用 UTF-8 without BOM

BOM检测命令：
```powershell
# 检测文件BOM（PowerShell）
$bom = Get-Content -Path "file.md" -Encoding Byte -ReadCount 4
if ($bom[0] -eq 0xEF -and $bom[1] -eq 0xBB -and $bom[2] -eq 0xBF) {
    "UTF-8 with BOM"
} elseif ($bom[0] -eq 0xFF -and $bom[1] -eq 0xFE) {
    "UTF-16"
} else {
    "UTF-8 without BOM or ASCII"
}
```

BOM修复命令：
```powershell
# 添加BOM（PowerShell）
$content = Get-Content -Path "file.md" -Raw
$encoding = New-Object System.Text.UTF8Encoding $true  # $true = with BOM
[System.IO.File]::WriteAllText("file.md", $content, $encoding)
```
```

### C1.2 Windows路径处理

```
Windows路径处理规则：

路径格式：
- Windows标准路径：C:\Users\user\...
- 反斜杠（\）：Windows路径分隔符
- 正斜杠（/）：Unix路径分隔符，Windows也支持但非标准

规则：
1. Windows环境写入路径 → 保持反斜杠原样
2. 不要将 C:\ 转换为 C:/
3. 使用 qclaw-text-file skill 脚本时 → 路径自动处理

错误示例：
```powershell
# 错误：将反斜杠转换为正斜杠
$path = "C:/Users/user/..."  # 可能在部分工具中失败
```

正确示例：
```powershell
# 正确：保持反斜杠
$path = "C:\Users\user\..."
```

路径处理代码示例：
```python
import os
# Windows路径处理
path = r"C:\Users\user\.qclaw\workspace"  # 原始字符串，避免转义
# 或
path = "/home/user\\.qclaw\\workspace"  # 转义
```
```

### C1.3 本次实战中文处理案例

```
本次实战中文内容写入记录：

案例1：stock-analyst.md 中文正文
- 文件编码：UTF-8 with BOM
- 中文内容：正确显示（如"护城河"、"估值倍数"）
- 验证：直接用记事本打开无乱码

案例2：宏公式文件（macro-formula.md）中文标注
- 文件编码：UTF-8 with BOM
- 公式：LaTeX（$M_2$等，不含中文）
- 中文标注：[增强来源：巴菲特《巴菲特致股东信》，1995]
- 验证：中文显示正常，公式渲染正常

错误案例记录：
- 错误：使用UTF-8 without BOM写入含中文markdown
- 症状：部分Windows工具打开显示乱码
- 修复：重新写入为UTF-8 with BOM
```
```

---

## C2. LaTeX公式嵌入规范

### C2.1 公式类型与语法

```
LaTeX公式嵌入规范：

行内公式：
- 语法：$formula$
- 示例：$NetIncome = Revenue - COGS - Expenses$
- 用途：公式嵌入正文中，不独立占行

块级公式：
- 语法：$$formula$$
- 示例：
$$
VaR_{\alpha} = \inf \{ x \in \mathbb{R} : P(L > x) \leq \alpha \}
$$
- 用途：重要公式独立展示，占据一行

嵌套规则：
- $ 和 $$ 不可嵌套
- 公式内使用 _ 表示下标（如 $M_2$）
- 公式内使用 ^ 表示上标（如 $R^2$）
- 公式内特殊字符需转义（_ → \_，^ →\^，$ →\$）

错误示例：
```markdown
# 错误：嵌套问题
$NetIncome = $Revenue$ - $COGS$  ← 嵌套错误

# 正确：
$NetIncome = Revenue - COGS - Expenses$
```

转义字符表：
| 符号 | 转义写法 | 说明 |
|-----|---------|------|
| _ | \_ | 下标 |
| ^ | \^ | 上标 |
| $ | \$ | 美元符号 |
| % | \% | 百分号 |
| # | \# | 井号 |
```

### C2.2 常见公式错误与修正

```
LaTeX公式常见错误：

错误类型1：中文变量名
问题：公式内使用中文变量名
错误示例：
```markdown
$净利润 = 收入 - 成本$  ← 中文变量名
```
修正示例：
```markdown
$NetIncome = Revenue - Cost$  ← 英文变量名
```

错误类型2：全角括号
问题：使用全角括号（）而非半角()
错误示例：
```markdown
$NetIncome = (Revenue - Cost)$  ← 全角括号
```
修正示例：
```markdown
$NetIncome = (Revenue - Cost)$  ← 半角括号
```

错误类型3：未转义的特殊字符
问题：下划线未转义
错误示例：
```markdown
$E_{net\_income}$  ← 正确转义
$E_{net_income}$  ← 未转义，编译可能失败
```

错误类型4：公式与中文之间缺少空格
问题：$符号紧邻中文字符
错误示例：
```markdown
净利润为$NetIncome$元  ← $紧邻中文
```
修正示例：
```markdown
净利润为 $NetIncome$ 元  ← $与中文之间有空格
```
```

### C2.3 公式检查命令

```
公式检查命令：

检查1：查找所有公式
```bash
# 查找行内公式
grep -n '\$[^\$]*\$' file.md | head -20

# 查找块级公式
grep -n '\$\$' file.md
```

检查2：查找可能的中文变量名（错误模式）
```bash
# Windows PowerShell：检测中文变量名
Select-String -Path "file.md" -Pattern '\$[^\$]*[\u4e00-\u9fa5][^\$]*\$'

# 或 grep（WSL环境）
grep -n '\$[^\$]*[\u4e00-\u9fa5][^\$]*\$' file.md
```

检查3：统计公式数量
```bash
# 统计行内公式数量
grep -c '\$[^\$]*\$' file.md

# 统计块级公式数量
grep -c '\$\$' file.md

# 总公式数
echo "行内公式：$(grep -c '\$[^\$]*\$' file.md)个"
echo "块级公式：$(grep -c '\$\$' file.md)个"
```

检查4：验证公式渲染（Q9质量门）
```bash
# 安装 LaTeX 渲染工具（可选）
# 检查公式内特殊字符转义
grep -n '\\' file.md | grep -v '\\\\' | head -10
# 说明：连续两个反斜杠才是转义后的单反斜杠
```

### C2.4 本次实战公式案例

```
本次实战公式处理记录：

案例1：stock-analyst.md 护城河分析
- 公式：无复杂公式，仅文字描述
- 来源：巴菲特1995《巴菲特致股东信》

案例2：macro-forecasting.md 宏观指标公式
- 公式：
  - $M_2 = Currency + Demand Deposits + Savings Deposits + Time Deposits$
  - $GDP_{real} = GDP_{nominal} / P_{index}$
  - $CPI = \frac{\sum P_t \times Q_t}{\sum P_0 \times Q_t} \times 100$
- 处理：全部使用英文变量名，无中文
- 渲染：Q9质量门通过（3个公式≥3个，需检查）

案例3：valuation-expert.md DCF公式
- 公式：
  - $DCF = \sum_{t=1}^{n} \frac{CF_t}{(1+WACC)^t}$
  - $TerminalValue = \frac{CF_{n+1}}{(WACC-g)}$
- 处理：英文变量名 + 希腊字母（WACC用英文缩写）
- 来源：Damodaran《投资估值》，2012

错误修正记录：
- 错误：初始版本使用 $净利润$
- 修正：改为 $NetIncome$
- 影响：避免跨平台渲染失败
```
```

---

## C3. 表格转换规则

### C3.1 表格类型选择

```
表格类型选择规则：

选择标准：
- 列数 ≤ 8列 → 可用 markdown表格 或 LaTeX表格
- 列数 > 8列 → 强制使用 markdown表格
- 含中文单元格 → 避免使用 LaTeX表格

表格类型对比：
┌────────────────┬─────────────────┬─────────────────┐
│ 表格类型        │ 优点            │ 缺点            │
├────────────────┼─────────────────┼─────────────────┤
│ Markdown表格   │ 通用性强、易维护│ 样式有限        │
│ LaTeX表格      │ 样式美观、学术感 │ 中文兼容性差    │
│ CSV表格        │ 数据处理方便    │ 需转换才能展示   │
└────────────────┴─────────────────┴─────────────────┘

推荐选择：
- 通用文档 → Markdown表格
- 学术论文 → LaTeX表格（但避免中文单元格）
- 数据分析 → CSV + Markdown展示
```

### C3.2 LaTeX表格规范

```
LaTeX表格规范：

基础语法：
```latex
\begin{table}[h]
\centering
\begin{tabular}{|c|c|c|}
\hline
Col1 & Col2 & Col3 \\
\hline
A & B & C \\
\hline
D & E & F \\
\hline
\end{tabular}
\caption{表格标题}
\end{table}
```

中文单元格处理（不推荐）：
- 问题：LaTeX中文字体配置复杂
- 备选方案1：使用英文替代中文（如"B"代替"是"）
- 备选方案2：改用Markdown表格

多列表头合并：
```latex
\usepackage{multirow}
MultiRowCells & MultiRowCells & \\
\hline
```

对齐方式：
- c：居中
- l：左对齐
- r：右对齐
```

### C3.3 Markdown表格规范

```
Markdown表格规范：

基础语法：
```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| A   | B   | C   |
| D   | E   | F   |
```

对齐语法：
```markdown
| 左对齐 | 居中 | 右对齐 |
|:-------|:----:|------:|
| A      |  B   |    C  |
```

列宽控制（部分渲染器支持）：
```markdown
| 列1（自动） | 列2（固定宽） |
|------------|----------------|
```

复杂表格示例（含中文）：
```markdown
| 指标名称 | 2023年 | 2024年 | 同比变化 |
|---------|--------|--------|---------|
| 净利润 | 100亿 | 120亿 | +20% |
| 营收   | 500亿 | 600亿 | +20% |
| 市盈率 | 15倍  | 12倍  | -20% |
```

本次实战表格案例：
```markdown
| 护城河类型 | 特征 | 典型企业 |
|-----------|------|---------|
| 无形资产 | 品牌溢价/专利保护 | 可口可乐/苹果 |
| 转换成本 | 客户粘性 | Salesforce/微软 |
| 网络效应 | 平台型业务 | 微信/亚马逊 |
| 成本优势 | 规模经济 | 沃尔玛/台积电 |
| 高效规模 | 细分市场利基 | 吉尼迪/喜诗糖果 |
```
```

### C3.4 表格转换工具

```
表格转换工具：

CSV → Markdown：
```python
import pandas as pd

# 读取CSV
df = pd.read_csv('data.csv')

# 输出Markdown
print(df.to_markdown(index=False))
```

Excel → Markdown：
```python
import pandas as pd

# 读取Excel
df = pd.read_excel('data.xlsx')

# 输出Markdown
print(df.to_markdown(index=False))
```

在线工具：
- TableConvert.com：CSV/Excel/LaTeX/Markdown互转
- Tables Generator：LaTeX表格在线生成
```

---

## C4. 三码混排一致性检查

### C4.1 混排场景识别

```
三码混排：中文正文 + 英文变量名 + LaTeX公式

典型场景：
场景1：中文正文描述 + 英文变量名 + LaTeX公式
```markdown
根据 DCF 公式 $$DCF = \sum_{t=1}^{n} \frac{CF_t}{(1+WACC)^t}$$，
计算得到 $NetIncome = 120$ 亿元。
```

场景2：纯英文变量名 + LaTeX公式
```markdown
The formula $E = mc^2$ describes mass-energy equivalence.
```

场景3：含中文变量名（错误）
```markdown
净利润为 $净利润$ 亿元。  ← 错误：中文变量名在LaTeX中
```
```

### C4.2 一致性检查规则

```
一致性检查规则：

规则1：中英文之间必须有空格
错误：净利润为$NetIncome$元
正确：净利润为 $NetIncome$ 元

规则2：变量名必须统一（要么全英文，要么全中文）
错误：$净利润$和$NetIncome$混用
正确：统一使用$NetIncome$

规则3：全角/半角一致性
错误：净利润为（120）亿元  ← 全角括号
正确：净利润为 (120) 亿元  ← 半角括号

规则4：括号匹配
错误：$NetIncome = (Revenue - Cost$  ← 不匹配
正确：$NetIncome = (Revenue - Cost)$  ← 匹配
```

### C4.3 自动化检查脚本

```powershell
# 三码混排一致性检查脚本（Windows PowerShell）

param(
    [string]$FilePath
)

Write-Host "=== 三码混排一致性检查 ===" -ForegroundColor Cyan
Write-Host "文件：$FilePath"
Write-Host ""

$content = Get-Content -Path $FilePath -Raw

# 检查1：中英文之间是否缺少空格
$pattern1 = '[\u4e00-\u9fa5][$A-Za-z]'
$pattern2 = '[$A-Za-z][\u4e00-\u9fa5]'
$matches1 = Select-String -InputObject $content -Pattern $pattern1 -AllMatches
$matches2 = Select-String -InputObject $content -Pattern $pattern2 -AllMatches

if ($matches1) {
    Write-Host "⚠️ 发现中文后紧跟英文（可能缺少空格）：" -ForegroundColor Yellow
    $matches1 | ForEach-Object { Write-Host "  第$($_.LineNumber)行：$($_.Line)" }
}

if ($matches2) {
    Write-Host "⚠️ 发现英文后紧跟中文（可能缺少空格）：" -ForegroundColor Yellow
    $matches2 | ForEach-Object { Write-Host "  第$($_.LineNumber)行：$($_.Line)" }
}

# 检查2：中文变量名
$pattern3 = '\$[^\$]*[\u4e00-\u9fa5][^\$]*\$'
$matches3 = Select-String -InputObject $content -Pattern $pattern3 -AllMatches

if ($matches3) {
    Write-Host "❌ 发现中文变量名（LaTeX中不允许）：" -ForegroundColor Red
    $matches3 | ForEach-Object { Write-Host "  第$($_.LineNumber)行：$($_.Line)" }
}

# 检查3：全角括号
$pattern4 = '（[^）]*）'  # 全角括号
$matches4 = Select-String -InputObject $content -Pattern $pattern4 -AllMatches

if ($matches4) {
    Write-Host "⚠️ 发现全角括号，建议替换为半角：" -ForegroundColor Yellow
    $matches4 | ForEach-Object { Write-Host "  第$($_.LineNumber)行：$($_.Line)" }
}

# 检查4：括号匹配
$openParens = ($content | Select-String -Pattern '\(' -AllMatches).Matches.Count
$closeParens = ($content | Select-String -Pattern '\)' -AllMatches).Matches.Count

if ($openParens -ne $closeParens) {
    Write-Host "❌ 括号不匹配：左括号$openParens个，右括号$closeParens个" -ForegroundColor Red
} else {
    Write-Host "✅ 括号匹配：$openParens 对" -ForegroundColor Green
}

Write-Host ""
Write-Host "检查完成" -ForegroundColor Cyan
```

---

## C5. 快速执行清单（多语言内容专用）

```
多语言内容审计快速执行清单：

□ C1.1：中文文件是否使用UTF-8 with BOM编码
□ C1.2：Windows路径是否保持反斜杠
□ C2.1：LaTeX公式语法正确（$...$ 嵌套无误）
□ C2.2：公式内无中文变量名
□ C2.3：特殊字符已转义（_ → \_）
□ C2.4：公式渲染测试通过
□ C3.1：表格列数≤8列
□ C3.2：含中文单元格避免使用LaTeX表格
□ C3.3：Markdown表格格式规范
□ C4.1：中英文之间有空格
□ C4.2：变量名统一（英文优先）
□ C4.3：全角/半角一致性
□ C4.4：括号匹配检查

执行优先级：C1 → C2 → C3 → C4
```

---

> 本增强层适用于 auditor 在审计含有多语言混排内容（中文+英文+LaTeX）时的标准化规则，基于 ClawTeam 知识库增强实战经验沉淀。