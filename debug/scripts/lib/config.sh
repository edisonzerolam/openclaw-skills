#!/usr/bin/env bash
# lib/config.sh — 加载 config.toml 到环境变量
# 简化 TOML 解析：支持 [section] 和 key = "value" 或 key = number
# 用法: source lib/config.sh <path-to-config.toml>

load_config() {
    local config_file="${1:-$(dirname "${BASH_SOURCE[0]}")/../config.toml}"
    [[ -f "$config_file" ]] || return $EX_CONFIG

    local section=""
    while IFS= read -r line; do
        # 跳过空行和注释
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue

        # section header
        if [[ "$line" =~ ^[[:space:]]*\[([a-zA-Z_][a-zA-Z0-9_]*)\][[:space:]]*$ ]]; then
            section="${BASH_REMATCH[1]}_"
            continue
        fi

        # key = value
        if [[ "$line" =~ ^[[:space:]]*([a-zA-Z_][a-zA-Z0-9_]*)[[:space:]]*=[[:space:]]*(.*)$ ]]; then
            local key="${section}${BASH_REMATCH[1]}"
            local val="${BASH_REMATCH[2]}"
            # 去除行尾注释
            val="${val%%#*}"
            val="${val%"${val##*[![:space:]]}"}"
            # 去除引号
            if [[ "$val" =~ ^\"(.*)\"$ ]] || [[ "$val" =~ ^\'(.*)\'$ ]]; then
                val="${BASH_REMATCH[1]}"
            fi
            # 转换 [a, b, c] 为空格分隔
            if [[ "$val" =~ ^\[(.*)\]$ ]]; then
                val="${BASH_REMATCH[1]}"
                val="${val//,/ }"
                val="${val//\"/}"
                val="${val//\'/}"
            fi
            export "$key"="$val"
        fi
    done < "$config_file"
    return $EX_OK
}

# 默认值（如果 config.toml 缺失）
defaults_pattern='ERROR|FATAL|Exception|Traceback|WARN|OOM|Segfault|panic|SIGKILL|SIGSEGV'
defaults_max_depth=5
defaults_max_lines=100000
http_default_timeout=10
http_check_timeout=10
leaks_default_duration=30
leaks_default_interval=5
leaks_leak_threshold_pct=20
leaks_warn_threshold_pct=5
profile_default_repeat=3
profile_fast_threshold_s=1.0
selfcheck_required_deps='bash python3 curl grep awk sed wc date'
selfcheck_expected_excodes='EX_OK EX_ERR_FOUND EX_WARN EX_PERM EX_TIMEOUT EX_CONFIG EX_USAGE'
selfcheck_expected_funcs='cmd_trace cmd_stacktrace cmd_leaks cmd_profile cmd_diff_logs cmd_http cmd_selfcheck cmd_format'
stacktrace_languages='python javascript java go c cpp'
