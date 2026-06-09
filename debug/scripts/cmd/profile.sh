#!/usr/bin/env bash
# cmd/profile.sh — measure command execution time and resources

cmd_profile() {
    local repeat="${profile_default_repeat:-3}"
    local cmd=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --repeat) repeat="$2"; shift 2 ;;
            *) cmd="$1"; shift ;;
        esac
    done

    if [[ -z "$cmd" ]]; then
        echo "Usage: debug profile [--repeat N] <command>" >&2
        return $EX_USAGE
    fi

    echo "=== Profiling: $cmd ==="
    echo "Runs: $repeat"
    echo ""

    local total_ms=0
    local min_ms=999999
    local max_ms=0
    local run=1
    local any_fail=0

    while [[ $run -le $repeat ]]; do
        local start_ns end_ns elapsed_ms
        start_ns=$(python3 -c 'import time; print(int(time.time()*1e9))' 2>/dev/null || date +%s%N 2>/dev/null)
        local exit_code=0

        eval "$cmd" > /dev/null 2>&1 || exit_code=$?

        end_ns=$(python3 -c 'import time; print(int(time.time()*1e9))' 2>/dev/null || date +%s%N 2>/dev/null)
        elapsed_ms=$(( (end_ns - start_ns) / 1000000 ))

        printf "Run %d: %dms (exit: %d)\n" "$run" "$elapsed_ms" "$exit_code"

        [[ $exit_code -ne 0 ]] && any_fail=1

        total_ms=$((total_ms + elapsed_ms))
        [[ $elapsed_ms -lt $min_ms ]] && min_ms=$elapsed_ms
        [[ $elapsed_ms -gt $max_ms ]] && max_ms=$elapsed_ms

        run=$((run + 1))
    done

    echo ""
    echo "--- Summary ---"
    local avg_ms=$((total_ms / repeat))
    echo "Avg:   ${avg_ms}ms"
    echo "Min:   ${min_ms}ms"
    echo "Max:   ${max_ms}ms"
    echo "Total: ${total_ms}ms"

    local fast_th_ms
    fast_th_ms=$(python3 -c "print(int(${profile_fast_threshold_s:-1.0} * 1000))" 2>/dev/null || echo "1000")
    if [[ $avg_ms -gt 5000 ]]; then
        echo "[SLOW] Average over 5 seconds"
    elif [[ $avg_ms -gt $fast_th_ms ]]; then
        echo "[MODERATE] Average over ${profile_fast_threshold_s:-1.0} second(s)"
    else
        echo "[FAST] Under ${profile_fast_threshold_s:-1.0} second(s)"
    fi

    [[ $any_fail -ne 0 ]] && return $EX_TIMEOUT || return $EX_OK
}
