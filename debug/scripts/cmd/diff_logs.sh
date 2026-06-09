#!/usr/bin/env bash
# cmd/diff_logs.sh — compare two log files, highlight new errors
# P2 新增: -r/--recursive 递归对比目录

cmd_diff_logs() {
    local errors_only=false
    local recursive=false
    local file1="" file2=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --errors-only) errors_only=true; shift ;;
            -r|--recursive) recursive=true; shift ;;
            *) [[ -z "$file1" ]] && file1="$1" || file2="$1"; shift ;;
        esac
    done

    if [[ -z "$file1" || -z "$file2" ]]; then
        echo "Usage: debug diff-logs [--errors-only] [-r] <file1|dir1> <file2|dir2>" >&2
        return $EX_USAGE
    fi

    # P2: -r 模式
    if [[ "$recursive" == true && (-d "$file1" || -d "$file2") ]]; then
        # 对目录下所有日志文件做两两对比
        local files1=() files2=()
        while IFS= read -r f; do files1+=("$f"); done < <(find_log_files "$file1")
        while IFS= read -r f; do files2+=("$f"); done < <(find_log_files "$file2")

        if [[ ${#files1[@]} -ne ${#files2[@]} ]]; then
            echo "Warning: file count mismatch (${#files1[@]} vs ${#files2[@]})" >&2
        fi

        local n=${#files1[@]}
        [[ ${#files2[@]} -lt $n ]] && n=${#files2[@]}

        for i in $(seq 0 $((n - 1))); do
            echo "=== Pair $((i + 1)): ${files1[$i]} vs ${files2[$i]} ==="
            _diff_logs_single "${files1[$i]}" "${files2[$i]}" "$errors_only"
        done
        return $EX_OK
    fi

    # 单文件对比
    _diff_logs_single "$file1" "$file2" "$errors_only"
    return $EX_OK
}

# Internal: 对单个文件对做 diff
_diff_logs_single() {
    local file1="$1"
    local file2="$2"
    local errors_only="$3"

    [[ -f "$file1" ]] || { echo "File not found: $file1" >&2; return $EX_USAGE; }
    [[ -f "$file2" ]] || { echo "File not found: $file2" >&2; return $EX_USAGE; }

    echo "=== Log Diff: $file1 vs $file2 ==="
    echo ""

    local lines1 lines2
    lines1=$(wc -l < "$file1")
    lines2=$(wc -l < "$file2")
    echo "Lines: $file1=$lines1, $file2=$lines2 (diff: $((lines2 - lines1)))"

    if [[ "$errors_only" == true ]]; then
        local err_pattern="ERROR\|FATAL\|Exception\|Traceback\|WARN"
        local errs1 errs2

        errs1=$(grep -c "$err_pattern" "$file1" 2>/dev/null || echo "0")
        errs2=$(grep -c "$err_pattern" "$file2" 2>/dev/null || echo "0")
        echo "Errors: $file1=$errs1, $file2=$errs2 (diff: $((errs2 - errs1)))"
        echo ""

        echo "--- New errors in $file2 ---"
        diff <(grep "$err_pattern" "$file1" 2>/dev/null | sort -u) \
             <(grep "$err_pattern" "$file2" 2>/dev/null | sort -u) 2>/dev/null | \
             grep "^>" | sed 's/^> //' | head -20
    else
        echo ""
        echo "--- New lines in $file2 ---"
        diff "$file1" "$file2" 2>/dev/null | grep "^>" | head -30 | sed 's/^> //'
        echo ""
        echo "--- Removed from $file1 ---"
        diff "$file1" "$file2" 2>/dev/null | grep "^<" | head -20 | sed 's/^< //'
    fi
}
