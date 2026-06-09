# Windows 调试增强知识库

> 版本：v1.0 | 状态：active | 更新：2026-05-25
> 定位：debug skill 的 Windows 环境增强模块

---

## 1. PowerShell 错误解析

### 触发词
`PowerShell 错误` / `ps1 报错` / `powershell trace`

### 错误特征
- `Get-Item : 该路径不存在`（PathNotFoundException）
- `UnauthorizedAccessException`（权限拒绝）
- `TerminatingError`（终止错误）
- `NonTerminatingError`（非终止错误）

### 诊断命令
```powershell
# 获取详细错误信息
$ErrorActionPreference = "Stop"
try { Get-Item "C:\nonexistent" } catch { $_.Exception.Message }
$Error[0] | Format-List * -Force

# 查看最近错误
$Error | Select-Object -First 5 Exception, ScriptStackTrace
```

---

## 2. `.ps1` 脚本性能分析

### 触发词
`ps1 性能` / `脚本执行慢` / `profile ps1`

### debug profile 命令用法
```bash
bash scripts/script.sh profile "powershell -File script.ps1"
```

### 快速诊断
```powershell
Measure-Command { & script.ps1 }
Trace-Command Expression profiler { & script.ps1 }
```

---

## 3. Windows BSOD/Minidump 解析

### 触发词
`蓝屏` / `BSOD` / `bsod` / `minidump`

### 快速检查
```bash
# 列出最近 minidump 文件
ls -la "C:\Windows\Minidump\"
```

### PowerShell 诊断
```powershell
Get-WinEvent -FilterHashtable @{LogName='System'; Id=1001} -MaxEvents 3 |
  Select-Object TimeCreated, Message
$dump = "C:\Windows\Minidump\Mini*.dmp"
if (Test-Path $dump) {
    $files = Get-Item $dump | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    "最新 Minidump: $($files.FullName) $($files.LastWriteTime)"
}
```

### 输出格式
```
BSOD 检测结果：
- 最新 Minidump: C:\Windows\Minidump\Mini062524-01.dmp (2024-06-25)
- 建议使用 WinDbg 分析完整崩溃堆栈
```

---

## 4. Windows 特定错误代码

| 代码 | 含义 | 常见场景 |
|------|------|---------|
| 0x80070005 | Access Denied | 文件/注册表缺权限 |
| 0x80070002 | File Not Found | 路径不存在 |
| 0x80070003 | Path Not Found | 目录不存在 |
| 0xC0000005 | Access Violation | 内存访问违规 |
| 0x80004005 | Unspecified Error | 需更多诊断 |

### 诊断命令
```powershell
[System.ComponentModel.Win32Exception]::new(0x80070005).Message
net helpmsg 5
```

---

*版本: v1.0 | 更新: 2026-05-25*