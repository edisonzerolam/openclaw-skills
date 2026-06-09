#!/usr/bin/env bash
# cmd/help.sh — show help

cmd_help() {
    cat << 'EOF'
debug v3.4.0 — Error tracing, log analysis, memory leak detection (P2 模块化)

Commands:
  trace         Find error patterns in log files (-r recursive)
  stacktrace    Parse and summarize stack traces / crash dumps
  leaks         Detect memory leaks by monitoring process RSS
  profile       Measure execution time and resource usage
  diff-logs     Compare two log files, highlight new errors (-r recursive)
  http          Debug HTTP requests (headers, timing, SSL, redirects, --check)
  selfcheck     P1-1: Validate the debug script itself (syntax/deps/exit codes)
  format        P1-2: Convert text input to JSON/CSV/Markdown table
  help          Show this help

Examples:
  debug trace /var/log/app.log
  debug trace -r /var/log/                           # P2: 递归整个目录
  debug trace --pattern "OOM|Segfault" --last 1h syslog
  debug stacktrace crash.log
  debug leaks --pid 1234 --duration 60
  debug profile --repeat 5 "curl -s https://api.example.com"
  debug diff-logs --errors-only old.log new.log
  debug diff-logs -r logs/old/ logs/new/              # P2: 递归目录对比
  debug http --verbose --timing https://example.com
  debug http --check https://api.example.com/health
  debug selfcheck
  debug format --output json --key hosts < hosts.txt

Configuration:
  Defaults in: scripts/config.toml
  Override:    edit config.toml (loaded at each call)

Module structure (P2):
  scripts/
    script.sh         # Main router (~50 lines)
    config.toml       # Default config
    lib/
      exit_codes.sh   # EX_OK, EX_ERR_FOUND, etc.
      config.sh       # TOML loader
      common.sh       # find_log_files, require_file, etc.
    cmd/
      trace.sh
      stacktrace.sh
      leaks.sh
      profile.sh
      diff_logs.sh
      http.sh
      selfcheck.sh
      format.sh
      help.sh

Powered by BytesAgain | bytesagain.com
EOF
}
