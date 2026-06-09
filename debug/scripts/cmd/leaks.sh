#!/usr/bin/env bash
# cmd/leaks.sh — monitor process memory over time
# 跨平台支持 (Linux/WSL/Windows)

# Platform detection
_leaks_is_windows() {
    if [[ -f /proc/version ]]; then
        grep -qi microsoft /proc/version 2>/dev/null && return 0
    fi
    [[ -n "${MSYSTEM:-}" || "${OSTYPE:-}" == msys || "${OSTYPE:-}" == cygwin ]] && return 0
    command -v tasklist.exe >/dev/null 2>&1 && return 0
    return 1
}

_leaks_process_exists() {
    local pid="$1"
    if _leaks_is_windows; then
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
        if command -v tasklist.exe >/dev/null 2>&1; then
            tasklist.exe /fi "PID eq $pid" 2>/dev/null | grep -qi "$pid"
            return $?
        fi
        return 1
    else
        kill -0 "$pid" 2>/dev/null
    fi
}

_leaks_get_process_name() {
    local pid="$1"
    if _leaks_is_windows; then
        wmic process where "processid=$pid" get name 2>/dev/null | tail -1 | tr -d ' \r\n' || echo "unknown"
    else
        ps -p "$pid" -o comm= 2>/dev/null || echo "unknown"
    fi
}

_leaks_get_memory() {
    local pid="$1"
    if _leaks_is_windows; then
        local info
        if command -v tasklist.exe >/dev/null 2>&1; then
            info=$(tasklist.exe /fi "PID eq $pid" /fo csv 2>/dev/null | tail -1)
            if [[ -n "$info" && "$info" != '""' ]]; then
                local rss
                rss=$(echo "$info" | awk -F',' '{gsub(/"/, "", $5); gsub(/[ K]/, "", $5); print $5}')
                rss=$(echo "$rss" | tr -d ',')
                echo "$rss 0"
                return 0
            fi
        fi
        ps -p "$pid" -o rss=,vsz= 2>/dev/null || echo "0 0"
    else
        ps -p "$pid" -o rss=,vsz= 2>/dev/null || echo "0 0"
    fi
}

cmd_leaks() {
    local pid=""
    local duration="${leaks_default_duration:-30}"
    local interval="${leaks_default_interval:-5}"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --pid) pid="$2"; shift 2 ;;
            --duration) duration="$2"; shift 2 ;;
            --interval) interval="$2"; shift 2 ;;
            *) pid="$1"; shift ;;
        esac
    done

    if [[ -z "$pid" ]]; then
        echo "Usage: debug leaks --pid <PID> [--duration 30] [--interval 5]" >&2
        return $EX_USAGE
    fi

    if ! _leaks_process_exists "$pid"; then
        echo "Process $pid not found" >&2
        return $EX_ERR_FOUND
    fi

    local cmd_name
    cmd_name=$(_leaks_get_process_name "$pid")
    echo "=== Memory Leak Detection ==="
    echo "PID: $pid ($cmd_name)"
    echo "Monitoring: ${duration}s at ${interval}s intervals"
    echo ""

    local samples=()
    local elapsed=0

    echo "Time       RSS(KB)    VSZ(KB)    Delta"
    echo "---------- ---------- ---------- ------"

    local prev_rss=0
    while [[ $elapsed -lt $duration ]]; do
        if ! _leaks_process_exists "$pid"; then
            echo "Process $pid exited during monitoring" >&2
            break
        fi

        local mem_info
        mem_info=$(_leaks_get_memory "$pid")
        local rss vsz
        rss=$(echo "$mem_info" | awk '{print $1}')
        vsz=$(echo "$mem_info" | awk '{print $2}')

        local delta=""
        if [[ $prev_rss -gt 0 ]]; then
            local diff=$((rss - prev_rss))
            if [[ $diff -gt 0 ]]; then
                delta="+${diff}"
            elif [[ $diff -lt 0 ]]; then
                delta="$diff"
            else
                delta="0"
            fi
        fi
        prev_rss=$rss

        printf "%-10s %-10s %-10s %s\n" "${elapsed}s" "$rss" "$vsz" "$delta"
        samples+=("$rss")

        sleep "$interval"
        elapsed=$((elapsed + interval))
    done

    echo ""
    if [[ ${#samples[@]} -ge 3 ]]; then
        local first=${samples[0]}
        local last=${samples[${#samples[@]}-1]}
        local growth=$((last - first))
        local growth_pct=0
        [[ $first -gt 0 ]] && growth_pct=$((growth * 100 / first))

        echo "--- Summary ---"
        echo "Start RSS: ${first}KB"
        echo "End RSS:   ${last}KB"
        echo "Growth:    ${growth}KB (${growth_pct}%)"

        local leak_th="${leaks_leak_threshold_pct:-20}"
        local warn_th="${leaks_warn_threshold_pct:-5}"
        if [[ $growth_pct -gt $leak_th ]]; then
            echo "[WARN] POSSIBLE LEAK: Memory grew ${growth_pct}% in ${duration}s"
            return $EX_ERR_FOUND
        elif [[ $growth_pct -gt $warn_th ]]; then
            echo "[WATCH] Memory grew ${growth_pct}%, monitor longer to confirm"
            return $EX_WARN
        else
            echo "[OK] Memory stable (${growth_pct}% change)"
            return $EX_OK
        fi
    fi
}
