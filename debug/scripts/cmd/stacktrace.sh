#!/usr/bin/env bash
# cmd/stacktrace.sh — parse and summarize a stack trace / crash dump
# 支持: python / java / javascript / go / c / c++

cmd_stacktrace() {
    local input="${1:--}"

    if [[ "$input" == "-" ]]; then
        local content
        content=$(cat)
    elif [[ -f "$input" ]]; then
        local content
        content=$(cat "$input")
    else
        echo "Usage: debug stacktrace <file|-> " >&2
        return $EX_USAGE
    fi

    echo "=== Stack Trace Analysis ==="
    echo ""

    # Detect language
    local lang="unknown"
    if echo "$content" | grep -q "Traceback (most recent call last)"; then
        lang="python"
    elif echo "$content" | grep -q "at .*(.*\.java:[0-9]*)"; then
        lang="java"
    elif echo "$content" | grep -q "at .*(.*\.[jt]s:[0-9]*)"; then
        lang="javascript"
    elif echo "$content" | grep -q "goroutine [0-9]*"; then
        lang="go"
    elif echo "$content" | grep -q "thread.*#[0-9]"; then
        lang="c/c++"
    fi
    echo "Language: $lang"

    # Extract error message
    echo ""
    echo "--- Error Message ---"
    case "$lang" in
        python)
            echo "$content" | tail -1
            echo ""
            echo "--- Call Chain (bottom = root cause) ---"
            echo "$content" | grep -E "File \"" | while IFS= read -r line; do
                local file_info
                file_info=$(echo "$line" | grep -oE "File \"[^\"]+\", line [0-9]+")
                local func
                func=$(echo "$line" | grep -oE "in [a-zA-Z_]+")
                echo "  $file_info $func"
            done
            ;;
        java)
            echo "$content" | head -1
            echo ""
            echo "--- Call Chain ---"
            echo "$content" | grep "^[[:space:]]*at " | head -10 | while IFS= read -r line; do
                echo "  $(echo "$line" | sed 's/^[[:space:]]*//')"
            done
            ;;
        javascript)
            echo "$content" | head -1
            echo ""
            echo "--- Call Chain ---"
            echo "$content" | grep "^[[:space:]]*at " | head -10 | while IFS= read -r line; do
                echo "  $(echo "$line" | sed 's/^[[:space:]]*//')"
            done
            ;;
        go)
            echo "$content" | grep -E "^(panic|fatal|runtime)" | head -1
            echo ""
            echo "--- Goroutine Info ---"
            echo "$content" | grep "goroutine " | head -5
            ;;
        *)
            echo "$content" | head -3
            ;;
    esac

    # Count frames
    local frames
    frames=$(echo "$content" | grep -cE "^[[:space:]]*(at |File \")" 2>/dev/null || echo "0")
    echo ""
    echo "Stack depth: $frames frames"
    return $EX_OK
}
