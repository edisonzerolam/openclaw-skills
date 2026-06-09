#!/usr/bin/env bash
# lib/common.sh — 通用辅助函数

# 获取脚本所在目录
script_dir() {
    cd "$(dirname "${BASH_SOURCE[0]}")" && pwd
}

# 递归查找日志文件（支持 glob）
# 用法: find_log_files <pattern> [max_depth]
find_log_files() {
    local pattern="$1"
    local max_depth="${2:-${defaults_max_depth:-5}}"

    if [[ -d "$pattern" ]]; then
        # 目录：递归查找 *.log 文件
        find "$pattern" -maxdepth "$max_depth" -type f \( -name "*.log" -o -name "*.txt" -o -name "*.out" \) 2>/dev/null
    elif [[ -f "$pattern" ]]; then
        echo "$pattern"
    elif [[ "$pattern" == "-" ]]; then
        echo "/dev/stdin"
    else
        # glob 展开
        for f in $pattern; do
            [[ -f "$f" ]] && echo "$f"
        done
    fi
}

# 检查文件存在 + 读权限
require_file() {
    local file="$1"
    if [[ -z "$file" ]]; then
        echo "Usage: file path required" >&2
        return $EX_USAGE
    fi
    if [[ ! -f "$file" ]]; then
        echo "File not found: $file" >&2
        return $EX_USAGE
    fi
    if [[ ! -r "$file" ]]; then
        echo "File not readable: $file" >&2
        return $EX_PERM
    fi
    return $EX_OK
}

# 时间戳
ts() {
    date '+%Y-%m-%d %H:%M:%S'
}
