#!/usr/bin/env bash
# cmd/http.sh — debug HTTP requests (headers, timing, SSL, redirects, --check)

cmd_http() {
    local url=""
    local verbose=false
    local timing=false
    local check_only=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --verbose) verbose=true; shift ;;
            --timing) timing=true; shift ;;
            --check) check_only=true; shift ;;
            *) url="$1"; shift ;;
        esac
    done

    if [[ -z "$url" ]]; then
        echo "Usage: debug http [--verbose] [--timing] [--check] <url>" >&2
        return $EX_USAGE
    fi

    # --check 模式：仅健康检查
    if [[ "$check_only" == true ]]; then
        echo "=== HTTP Health Check: $url ==="
        local status
        status=$(curl -s -o /dev/null -w "%{http_code}" --max-time "${http_check_timeout:-10}" "$url" 2>/dev/null || echo "000")
        local elapsed
        elapsed=$(curl -s -o /dev/null -w "%{time_total}" --max-time "${http_check_timeout:-10}" "$url" 2>/dev/null || echo "0")
        echo "URL:      $url"
        echo "Status:   $status"
        echo "Response: ${elapsed}s"
        if [[ "$status" -ge 200 && "$status" -lt 400 ]]; then
            echo "Result:   [HEALTHY]"
            return $EX_OK
        else
            echo "Result:   [UNHEALTHY]"
            return $EX_ERR_FOUND
        fi
    fi

    echo "=== HTTP Debug: $url ==="
    echo ""

    # Basic request
    local status
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time "${http_default_timeout:-10}" "$url" 2>/dev/null || echo "000")
    echo "Status: $status"

    # Timing
    if [[ "$timing" == true ]]; then
        echo ""
        echo "--- Timing ---"
        curl -s -o /dev/null -w \
            "DNS:        %{time_namelookup}s\nConnect:    %{time_connect}s\nTLS:        %{time_appconnect}s\nFirstByte:  %{time_starttransfer}s\nTotal:      %{time_total}s\nSize:       %{size_download} bytes\n" \
            --max-time "${http_default_timeout:-10}" \
            "$url" 2>/dev/null
    fi

    # Headers
    if [[ "$verbose" == true ]]; then
        echo ""
        echo "--- Response Headers ---"
        curl -sI --max-time "${http_default_timeout:-10}" "$url" 2>/dev/null | head -20
    fi

    # SSL info
    if [[ "$url" == https://* ]]; then
        echo ""
        echo "--- SSL ---"
        local ssl_info
        ssl_info=$(curl -s -o /dev/null -w "Protocol: %{ssl_verify_result}\n" --max-time "${http_default_timeout:-10}" "$url" 2>/dev/null)
        echo "$ssl_info"

        local expiry
        expiry=$(echo | openssl s_client -connect "${url#https://}:443" -servername "${url#https://}" 2>/dev/null | \
                 openssl x509 -noout -dates 2>/dev/null | grep "notAfter" | cut -d= -f2)
        [[ -n "$expiry" ]] && echo "Cert expires: $expiry"
    fi

    # Redirect chain
    echo ""
    echo "--- Redirects ---"
    curl -sIL --max-time "${http_default_timeout:-10}" "$url" 2>/dev/null | grep -E "^(HTTP/|Location:)" | head -10

    [[ "$status" -ge 400 ]] && return $EX_ERR_FOUND
    return $EX_OK
}
