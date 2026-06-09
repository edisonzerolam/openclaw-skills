#!/usr/bin/env bash
# cmd/trace.sh — find error patterns in log files
# 用法: debug trace [--pattern REGEX] [--last 1h|30m|2d] [-r] <logfile|directory>
# P2 新增: -r/--recursive 递归处理目录

cmd_trace() {
    local pattern="${defaults_pattern:-ERROR|FATAL|Exception|Traceback|WARN|OOM|Segfault|panic|SIGKILL|SIGSEGV}"
    local time_filter=""
    local target=""
    local recursive=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --pattern) pattern="$2"; shift 2 ;;
            --last)
                local duration="$2"
                local unit="${duration: -1}"
                local num="${duration%?}"
                case "$unit" in
                    h) time_filter=$(date -d "$num hours ago" '+%Y-%m-%d %H' 2>/dev/null || date -v-"${num}H" '+%Y-%m-%d %H' 2>/dev/null || echo "") ;;
                    m) time_filter=$(date -d "$num minutes ago" '+%Y-%m-%d %H:%M' 2>/dev/null || echo "") ;;
                    d) time_filter=$(date -d "$num days ago" '+%Y-%m-%d' 2>/dev/null || echo "") ;;
                    *) time_filter="" ;;
                esac
                shift 2 ;;
            -r|--recursive) recursive=true; shift ;;
            *) target="$1"; shift ;;
        esac
    done

    if [[ -z "$target" ]]; then
        echo "Usage: debug trace [--pattern REGEX] [--last 1h|30m|2d] [-r] <logfile|directory>" >&2
        return $EX_USAGE
    fi

    # 解析文件列表（支持 -r 递归）
    local files=()
    if [[ "$recursive" == true && -d "$target" ]]; then
        while IFS= read -r f; do
            files+=("$f")
        done < <(find_log_files "$target" "${defaults_max_depth:-5}")
    else
        while IFS= read -r f; do
            files+=("$f")
        done < <(find_log_files "$target")
    fi

    if [[ ${#files[@]} -eq 0 ]]; then
        echo "No files found: $target" >&2
        return $EX_USAGE
    fi

    local total_match=0
    for file in "${files[@]}"; do
        if [[ ! -f "$file" || ! -r "$file" ]]; then
            echo "Skip: $file (not found or not readable)" >&2
            continue
        fi
        local total_lines
        total_lines=$(wc -l < "$file" 2>/dev/null || echo "0")
        echo "=== Debug Trace: $file ==="
        echo "Total lines: $total_lines"
        echo "Pattern: $pattern"
        echo ""

        local match_count
        if [[ -n "$time_filter" ]]; then
            match_count=$(grep "$time_filter" "$file" 2>/dev/null | grep -c "$pattern" 2>/dev/null || echo "0")
            echo "Time filter: since $time_filter"
        else
            match_count=$(grep -c "$pattern" "$file" 2>/dev/null || echo "0")
        fi
        echo "Matches: $match_count"
        echo ""

        echo "--- Error Breakdown ---"
        grep -oE "(ERROR|FATAL|Exception|Traceback|WARN|OOM|Segfault|panic|SIGKILL|SIGSEGV)" "$file" 2>/dev/null | sort | uniq -c | sort -rn | head -10
        echo ""

        echo "--- Last 20 Matches ---"
        if [[ -n "$time_filter" ]]; then
            grep "$time_filter" "$file" 2>/dev/null | grep "$pattern" 2>/dev/null | tail -20
        else
            grep "$pattern" "$file" 2>/dev/null | tail -20
        fi
        echo ""

        echo "--- Unique Error Patterns (top 10) ---"
        if [[ -n "$time_filter" ]]; then
            grep "$time_filter" "$file" 2>/dev/null | grep "$pattern" 2>/dev/null
        else
            grep "$pattern" "$file" 2>/dev/null
        fi | sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}[T ][0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}[^ ]*/TIMESTAMP/g' | \
            sed 's/0x[0-9a-fA-F]*/0xADDR/g' | \
            sed 's/pid=[0-9]*/pid=N/g' | \
            sort | uniq -c | sort -rn | head -10

        total_match=$((total_match + match_count))
    done

    echo ""
    echo "=== TOTAL: $total_match matches across ${#files[@]} file(s) ==="
    [[ "$total_match" -gt 0 ]] && return $EX_ERR_FOUND || return $EX_OK
}
