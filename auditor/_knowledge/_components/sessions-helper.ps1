# sessions-helper.ps1 — S2/S4 Sub-Agent Coordinator
# Version: 1.0 | For auditor S2/S4 + agent-planner F11/E6
# Usage: sessions-helper.ps1 -Mode <Single|Parallel|Pipeline> -Tasks <Task[]> [-MaxConcurrency N]

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("Single", "Parallel", "Pipeline")]
    [string]$Mode,

    [Parameter(Mandatory=$false)]
    [string[]]$Tasks = @(),

    [Parameter(Mandatory=$false)]
    [string[]]$AgentIds = @(),

    [Parameter(Mandatory=$false)]
    [int]$MaxConcurrency = 4,

    [Parameter(Mandatory=$false)]
    [int]$Timeout = 120,

    [Parameter(Mandatory=$false)]
    [string]$RunId = "",

    [Parameter(Mandatory=$false)]
    [string]$SkillDir = "$HOME\.qclaw\skills"
)

$ErrorActionPreference = "SilentlyContinue"

function Write-Log {
    param([string]$msg, [string]$level = "INFO")
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts] [$level] $msg"
}

# === Single mode: serial sessions_spawn ===
function Invoke-Single {
    param([string]$task, [string]$agentId = "scuttle", [int]$timeout = 120)
    Write-Log "Single mode: spawning $agentId for 1 task" "EXEC"
    try {
        $result = openclaw sessions spawn --name "$agentId" --message "$task" --timeout $timeout --json 2>&1
        return @{ status = "ok"; output = $result; agent = $agentId }
    } catch {
        return @{ status = "error"; output = $_.Exception.Message; agent = $agentId }
    }
}

# === Parallel mode: Start-Job based parallel sessions_spawn ===
function Invoke-Parallel {
    param([string[]]$taskList, [string[]]$agentIdList, [int]$maxConcurrency = 4, [int]$timeout = 120)

    Write-Log "Parallel mode: $($taskList.Count) tasks, concurrency=$maxConcurrency" "EXEC"

    $jobs = @()
    $results = @()
    $seq = 1

    for ($i = 0; $i -lt $taskList.Count; $i++) {
        $task = $taskList[$i]
        $agentId = if ($agentIdList.Count -gt $i) { $agentIdList[$i] } else { "scuttle" }
        $name = "$agentId-$seq"

        Write-Log "Spawning $name (timeout=${timeout}s)" "SPAWN"
        $seq++

        $job = Start-Job -ScriptBlock {
            param($task, $agentId, $name, $timeout, $openclawPath)
            Set-Location $openclawPath
            $env:PATH = "$HOME\node;$env:PATH"
            try {
                $out = openclaw sessions spawn --name "$name" --message "$task" --timeout $timeout 2>&1
                return @{ status = "ok"; name = $name; output = $out }
            } catch {
                return @{ status = "error"; name = $name; output = $_.Exception.Message }
            }
        } -ArgumentList $task, $agentId, $name, $timeout, (Get-Location).Path

        $jobs += @{ job = $job; name = $name }
    }

    # Wait and collect results
    $completed = @()
    foreach ($j in $jobs) {
        $started = Get-Date
        $result = $null
        while ((Get-Job -Id $j.job.Id).State -eq "Running") {
            if (((Get-Date) - $started).TotalSeconds -gt $timeout) {
                Stop-Job -Id $j.job.Id
                $result = @{ status = "timeout"; name = $j.name; output = "Timeout after ${timeout}s" }
                break
            }
            Start-Sleep -Milliseconds 200
        }
        if ($null -eq $result) {
            $result = Receive-Job -Job $j.job
        }
        Remove-Job -Job $j.job -Force
        $completed += $result
        Write-Log "Finished: $($j.name) → $($result.status)" "DONE"
    }

    return $completed
}

# === Pipeline mode: serial with result passing ===
function Invoke-Pipeline {
    param([string[]]$taskList, [string[]]$agentIdList, [int]$timeout = 120)

    Write-Log "Pipeline mode: $($taskList.Count) stages, serial" "EXEC"

    $prevResult = $null
    $seq = 1
    $results = @()

    for ($i = 0; $i -lt $taskList.Count; $i++) {
        $task = $taskList[$i]
        $agentId = if ($agentIdList.Count -gt $i) { $agentIdList[$i] } else { "scuttle" }
        $name = "$agentId-pipeline-$seq"

        # Prepend previous result if pipeline output exists
        $fullTask = $task
        if ($prevResult) {
            $fullTask = "Previous stage result:`n$($prevResult.output)`n`nNext task:`n$task"
        }

        Write-Log "Pipeline stage $seq: $name" "EXEC"
        try {
            $out = openclaw sessions spawn --name "$name" --message "$fullTask" --timeout $timeout 2>&1
            $prevResult = @{ status = "ok"; output = $out; name = $name }
        } catch {
            $prevResult = @{ status = "error"; output = $_.Exception.Message; name = $name }
        }

        $results += $prevResult
        $seq++
    }

    return $results
}

# === Main ===
Write-Log "sessions-helper.ps1 v1.0 | Mode=$Mode Tasks=$($Tasks.Count)" "START"

if ($Tasks.Count -eq 0) {
    Write-Log "No tasks provided" "ERROR"
    exit 1
}

$output = @{ mode = $Mode; timestamp = (Get-Date).ToString("o"); tasks = $Tasks.Count }

switch ($Mode) {
    "Single" {
        $result = Invoke-Single -task $Tasks[0] -agentId ($AgentIds[0] -or "scuttle") -timeout $Timeout
        $output.result = @($result)
    }
    "Parallel" {
        $result = Invoke-Parallel -taskList $Tasks -agentIdList $AgentIds -maxConcurrency $MaxConcurrency -timeout $Timeout
        $output.results = $result
    }
    "Pipeline" {
        $result = Invoke-Pipeline -taskList $Tasks -agentIdList $AgentIds -timeout $Timeout
        $output.results = $result
    }
}

$output | ConvertTo-Json -Depth 4
Write-Log "Done. $($output.results.Count) results" "FINISH"
exit 0