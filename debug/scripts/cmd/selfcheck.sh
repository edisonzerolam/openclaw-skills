#!/usr/bin/env bash
# cmd/selfcheck.sh — validate the debug script itself
# P2 更新: 路径使用 SCRIPT_DIR，支持分散模块

cmd_selfcheck() {
    echo "=== Debug Self-Check ==="
    echo ""
    local fail=0

    # 1. bash 语法检查（对所有 .sh 文件）
    echo "--- 1. Bash 语法检查 ---"
    local syntax_ok=true
    for sh_file in "$SCRIPT_DIR"/script.sh "$SCRIPT_DIR"/lib/*.sh "$SCRIPT_DIR"/cmd/*.sh; do
        if [[ -f "$sh_file" ]]; then
            if bash -n "$sh_file" 2>/dev/null; then
                echo "  [OK] $(basename "$sh_file")"
            else
                echo "  [FAIL] $(basename "$sh_file")" >&2
                fail=1
                syntax_ok=false
            fi
        fi
    done
    $syntax_ok && echo "[OK] 全部语法通过" || echo "[FAIL] 有语法错误" >&2

    # 2. 关键命令可用性
    echo ""
    echo "--- 2. 依赖命令可用性 ---"
    local deps=(${selfcheck_required_deps:-bash python3 curl grep awk sed wc date})
    for cmd in "${deps[@]}"; do
        if command -v "$cmd" >/dev/null 2>&1; then
            echo "  [OK] $cmd: $(command -v "$cmd")"
        else
            echo "  [MISS] $cmd: NOT FOUND"
            fail=1
        fi
    done

    # 3. 退出码常量定义检查
    echo ""
    echo "--- 3. 退出码常量检查 ---"
    local expected_excodes=(${selfcheck_expected_excodes:-EX_OK EX_ERR_FOUND EX_WARN EX_PERM EX_TIMEOUT EX_CONFIG EX_USAGE})
    for ex in "${expected_excodes[@]}"; do
        if declare -F "EX_$ex" >/dev/null 2>&1 || grep -qE "^declare -r $ex=" "$SCRIPT_DIR/lib/exit_codes.sh"; then
            echo "  [OK] $ex: 已定义"
        else
            echo "  [MISS] $ex: 缺失" >&2
            fail=1
        fi
    done

    # 4. 关键命令函数存在性
    echo ""
    echo "--- 4. 关键函数检查 ---"
    local expected_funcs=(${selfcheck_expected_funcs:-cmd_trace cmd_stacktrace cmd_leaks cmd_profile cmd_diff_logs cmd_http cmd_selfcheck cmd_format})
    for fn in "${expected_funcs[@]}"; do
        if declare -f "$fn" >/dev/null 2>&1; then
            echo "  [OK] $fn: 已加载"
        else
            echo "  [MISS] $fn: 缺失" >&2
            fail=1
        fi
    done

    # 5. 帮助命令可调用
    echo ""
    echo "--- 5. 帮助命令测试 ---"
    if bash "$SCRIPT_DIR/script.sh" help >/dev/null 2>&1; then
        echo "  [OK] help 命令可执行"
    else
        echo "  [FAIL] help 命令执行失败" >&2
        fail=1
    fi

    # 6. 脚本版本
    echo ""
    echo "--- 6. 版本信息 ---"
    local ver
    ver=$(grep -E "^VERSION=" "$SCRIPT_DIR/script.sh" | head -1 | cut -d'"' -f2)
    echo "脚本版本: $ver"

    # 7. 配置加载（新增）
    echo ""
    echo "--- 7. 配置加载 ---"
    if [[ -f "$SCRIPT_DIR/config.toml" ]]; then
        echo "  [OK] config.toml 存在"
    else
        echo "  [WARN] config.toml 缺失，使用默认值"
    fi

    echo ""
    if [[ $fail -eq 0 ]]; then
        echo "[OK] ALL CHECKS PASSED"
        return $EX_OK
    else
        echo "[FAIL] SELF-CHECK FAILED" >&2
        return $EX_ERR_FOUND
    fi
}
