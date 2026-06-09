#!/usr/bin/env bash
# lib/exit_codes.sh — Debug Skill 退出码常量
# P1-4 统一退出码 (2026-06-05)
# 所有命令函数应 return $EX_* 而不是 return EX_*
# 修复: 之前所有 return EX_* 因 bash 不展开无 $ 前缀的变量，已改为 return $EX_*

declare -r EX_OK=0           # 干净 / 成功
declare -r EX_ERR_FOUND=1    # 检测到问题（trace 找到错误 / http 4xx5xx / leaks >20%）
declare -r EX_WARN=2         # 警告（leaks 5-20% 增长等）
declare -r EX_PERM=3         # 权限拒绝
declare -r EX_TIMEOUT=4      # 超时 / 被 profile 的命令非零退出
declare -r EX_CONFIG=5       # 配置错误
declare -r EX_USAGE=64       # 用法错误（命令行参数缺失/无效）
