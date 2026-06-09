#!/usr/bin/env bash
# debug — error tracing, log analysis, memory leak detection, HTTP debugging
# v3.4.0 (P2 重构 - 模块化)
# 拆分: lib/exit_codes.sh / lib/config.sh / lib/common.sh / cmd/*.sh
set -euo pipefail
VERSION="3.4.0"

# === 定位脚本目录 ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# === 加载模块 ===
# 1. 退出码常量（最优先，所有命令都依赖）
# shellcheck source=lib/exit_codes.sh
source "$SCRIPT_DIR/lib/exit_codes.sh"

# 2. 配置加载器
# shellcheck source=lib/config.sh
source "$SCRIPT_DIR/lib/config.sh"

# 3. 通用辅助函数
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

# 4. 加载配置
load_config "$SCRIPT_DIR/config.toml" || echo "Warning: config.toml not found, using defaults" >&2

# === 加载命令模块 ===
for cmd_file in "$SCRIPT_DIR"/cmd/*.sh; do
    [[ -f "$cmd_file" ]] || continue
    # shellcheck source=/dev/null
    source "$cmd_file"
done

# === 主路由 ===
case "${1:-help}" in
    trace)      shift; cmd_trace "$@" ;;
    stacktrace) shift; cmd_stacktrace "$@" ;;
    leaks)      shift; cmd_leaks "$@" ;;
    profile)    shift; cmd_profile "$@" ;;
    diff-logs)  shift; cmd_diff_logs "$@" ;;
    http)       shift; cmd_http "$@" ;;
    selfcheck)  shift; cmd_selfcheck "$@" ;;
    format)     shift; cmd_format "$@" ;;
    help|*)     cmd_help ;;
esac
