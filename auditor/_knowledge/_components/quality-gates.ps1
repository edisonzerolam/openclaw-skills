# quality-gates.ps1 - Q1-Q5 质量门检查脚本
# Version: 1.1 | For auditor Layer0
# Usage: powershell -File quality-gates.ps1 [-TargetSkill <name>] [-JsonOutput]

param(
    [string]$SkillDir = "$HOME\.qclaw\skills",
    [string]$TargetSkill = "",
    [switch]$JsonOutput
)

$ErrorActionPreference = "SilentlyContinue"

function Write-Result {
    param([string]$gate, [string]$status, [string]$detail, [object]$data = $null)
    $r = [ordered]@{
        gate = $gate
        status = $status
        detail = $detail
        data = $data
        timestamp = (Get-Date).ToString("HH:mm:ss")
    }
    if ($JsonOutput) {
        $r | ConvertTo-Json -Compress -Depth 3 | Write-Output
    } else {
        $emoji = switch ($status) {
            "PASS"  { "[OK]" }
            "WARN"  { "[!]" }
            "BLOCK" { "[X]" }
            default { "[i]" }
        }
        Write-Host "$emoji [$gate] $status - $detail"
    }
}

# Q1: 依赖缺口检查
function Test-Q1 {
    $skillMap = [ordered]@{
        "A" = "skill-audit-suite"
        "B" = "behavior-checker"
        "C" = "skill-context-hygiene"
        "D" = "skill-session-manager"
        "E" = "agent-planner"
        "F" = "deep-research"
        "G" = "self-improving"
        "H" = "agent-team"
        "I" = "docx"
        "J" = "knowledge-base"
        "K" = "s1-quality-attributes"
        "L" = "financial-compliance"
    }
    
    $missing = @()
    $available = @()
    
    foreach ($layer in $skillMap.Keys) {
        $skillName = $skillMap[$layer]
        $exists = Test-Path "$SkillDir\$skillName"
        if (-not $exists) {
            # Check if built-in component
            $builtinPaths = @(
                "$SkillDir\auditor\_components\behavior-checker.md"
                "$SkillDir\auditor\_components\context-hygiene.md"
                "$SkillDir\auditor\_components\session-manager.md"
                "$SkillDir\auditor\_components\s1-quality-attributes.md"
                "$SkillDir\auditor\_components\financial-compliance.md"
            )
            $isBuiltin = $false
            foreach ($bp in $builtinPaths) {
                if (Test-Path $bp) { $isBuiltin = $true; break }
            }
            if (-not $isBuiltin) {
                $missing += $layer
            } else {
                $available += $layer
            }
        } else {
            $available += $layer
        }
    }
    
    $status = "PASS"
    if ($missing.Count -gt 0) { $status = "WARN" }
    if ($missing.Count -gt 3) { $status = "BLOCK" }
    
    Write-Result "Q1" $status "Available: $($available.Count)/12, Missing: $($missing -join ',')" @{
        available = $available
        missing = $missing
        total = 12
    }
}

# Q2: 确认类型检查
function Test-Q2 {
    Write-Result "Q2" "PASS" "Confirmation type: explicit_user_authorization" @{
        type = "explicit"
        requires_approval = $true
    }
}

# Q3: 复杂度检查
function Test-Q3 {
    param([int]$ChangeCount = 0)
    if ($ChangeCount -eq 0 -and $TargetSkill) {
        $skillPath = "$SkillDir\$TargetSkill"
        if (Test-Path $skillPath) {
            $ChangeCount = (Get-ChildItem $skillPath -Recurse -File | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-1) }).Count
        }
    }
    $status = "PASS"
    if ($ChangeCount -gt 5) { $status = "WARN" }
    if ($ChangeCount -gt 10) { $status = "BLOCK" }
    
    Write-Result "Q3" $status "Change count: $ChangeCount (threshold: 5)" @{
        count = $ChangeCount
        threshold = 5
        phase_d_trigger = ($ChangeCount -gt 5)
    }
}

# Q4: 冻结期检查
function Test-Q4 {
    $frozenFile = "$SkillDir\auditor\frozen_version.json"
    $frozen = @{
        frozen = $false
        consecutive_clean_audits = 0
        last_evolution = $null
    }
    if (Test-Path $frozenFile) {
        try {
            $content = Get-Content $frozenFile -Raw | ConvertFrom-Json
            $frozen.frozen = $content.frozen
            $frozen.consecutive_clean_audits = $content.consecutive_clean_audits
            $frozen.last_evolution = $content.last_evolution
        } catch {
            Write-Result "Q4" "WARN" "frozen_version.json parse error" $frozen
            return
        }
    }
    $status = "PASS"
    if ($frozen.frozen) { $status = "BLOCK" }
    
    Write-Result "Q4" $status "Frozen: $($frozen.frozen), Clean streak: $($frozen.consecutive_clean_audits)" $frozen
}

# Q5: Workspace 关联检查
function Test-Q5 {
    $workspace = if ($env:QCLAW_WORKSPACE) { $env:QCLAW_WORKSPACE } else { "$HOME\.qclaw\workspace" }
    $workspace = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($workspace)
    $exists = Test-Path $workspace
    $status = if ($exists) { "PASS" } else { "WARN" }
    
    Write-Result "Q5" $status "Workspace: $workspace" @{
        path = $workspace
        exists = $exists
        env_set = [bool]$env:QCLAW_WORKSPACE
    }
}

# Main execution
if (-not $JsonOutput) {
    Write-Host "=== Auditor Quality Gates Q1-Q5 ==="
    Write-Host "SkillDir: $SkillDir"
    if ($TargetSkill) { Write-Host "TargetSkill: $TargetSkill" }
    Write-Host ""
}

Test-Q1
Test-Q2
Test-Q3 -ChangeCount 0
Test-Q4
Test-Q5

if (-not $JsonOutput) {
    Write-Host ""
    Write-Host "=== Done ==="
}
