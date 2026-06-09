#!/usr/bin/env bash
# cmd/format.sh — convert text input to JSON/CSV/Markdown table
# P2 新增: -r/--recursive 处理目录

cmd_format() {
    local input_format="text"
    local output_format="json"
    local input="-"
    local key=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --input) input_format="$2"; shift 2 ;;
            --output) output_format="$2"; shift 2 ;;
            --key) key="$2"; shift 2 ;;
            *) input="$1"; shift ;;
        esac
    done

    # 读取输入
    local content
    if [[ "$input" == "-" ]]; then
        content=$(cat)
    elif [[ -f "$input" ]]; then
        content=$(cat "$input")
    else
        echo "Usage: debug format [--input text|lines] [--output json|csv|md] [--key NAME] <file|->" >&2
        return $EX_USAGE
    fi

    case "$output_format" in
        json)
            if [[ -n "$key" ]]; then
                echo "{"
                echo "  \"$key\": ["
                echo "$content" | awk 'NF{printf "    \"%s\",\n", $0}' | sed '$ s/,$//'
                echo "  ]"
                echo "}"
            else
                echo "["
                echo "$content" | awk 'NF{printf "  \"%s\",\n", $0}' | sed '$ s/,$//'
                echo "]"
            fi
            ;;
        csv)
            if [[ -n "$key" ]]; then
                echo "$key"
            fi
            echo "$content"
            ;;
        md)
            if [[ -n "$key" ]]; then
                echo "| $key |"
                echo "| --- |"
            else
                echo "| Item |"
                echo "| --- |"
            fi
            echo "$content" | awk 'NF{printf "| %s |\n", $0}'
            ;;
        *)
            echo "Unknown output format: $output_format (use json|csv|md)" >&2
            return $EX_USAGE
            ;;
    esac
    return $EX_OK
}
