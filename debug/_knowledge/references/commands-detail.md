# debug 命令参考

## trace — 日志错误分析

```bash
bash scripts/script.sh trace /var/log/app.log
bash scripts/script.sh trace --pattern "OOM|Segfault|FATAL" /var/log/syslog
bash scripts/script.sh trace --last 1h /var/log/app.log
bash scripts/script.sh trace -r /var/log/          # 递归目录
```

## stacktrace — 堆栈解析

```bash
bash scripts/script.sh stacktrace crash.log
echo "TypeError: cannot read property 'x' of undefined\n    at foo (app.js:42)" | bash scripts/script.sh stacktrace -
```

## leaks — 内存泄漏检测

```bash
bash scripts/script.sh leaks --pid 1234
bash scripts/script.sh leaks --pid 1234 --duration 60 --interval 5
```

## profile — 性能剖析

```bash
bash scripts/script.sh profile "python3 slow_script.py"
bash scripts/script.sh profile --repeat 5 "curl -s https://api.example.com"
```

## diff-logs — 日志差异对比

```bash
bash scripts/script.sh diff-logs before.log after.log
bash scripts/script.sh diff-logs --errors-only old.log new.log
bash scripts/script.sh diff-logs -r old_dir/ new_dir/   # 递归目录
```

## http — HTTP 调试

```bash
bash scripts/script.sh http https://example.com
bash scripts/script.sh http --verbose --timing https://api.example.com/health
bash scripts/script.sh http --check https://api.example.com/health   # P1-3: HEAD 健康检查
bash scripts/script.sh http --ssl https://example.com                # SSL 深度检查
bash scripts/script.sh http --redirects https://example.com          # 重定向链
bash scripts/script.sh http --headers https://example.com            # 请求/响应头
```

## selfcheck — 脚本自检

```bash
bash scripts/script.sh selfcheck
# 7 项检查: 语法 / 依赖 / 退出码常量 / 关键函数 / help / 版本 / 配置
# 返回 0 = 全部通过, 1 = 有缺失
```

## format — 结构化输出

```bash
cat hosts.txt | bash scripts/script.sh format --output json
cat hosts.txt | bash scripts/script.sh format --output json --key hosts
cat hosts.txt | bash scripts/script.sh format --output csv --key fruit
cat hosts.txt | bash scripts/script.sh format --output md --key item
```

## config.toml 配置

| 段落 | 键 | 默认值 | 说明 |
|------|-----|--------|------|
| defaults | pattern | `ERROR\|FATAL\|...` | trace 默认正则 |
| defaults | max_depth | 5 | 递归最大深度 |
| http | default_timeout | 10 | HTTP 超时秒数 |
| http | check_timeout | 10 | --check 超时秒数 |
| leaks | default_duration | 30 | 监测时长秒数 |
| leaks | leak_threshold_pct | 20 | 泄漏判定百分比 |
| profile | default_repeat | 3 | 重复次数 |
| selfcheck | required_deps | bash python3 curl... | 依赖列表 |

## 并行支持（`[[PARALLEL]]`）

| 命令 | 并行模式 |
|------|---------|
| `leaks` | 多进程同时监控 (--pid A & --pid B) |
| `profile` | 多命令同时度量 (--repeat 5 x2) |
| `http` | 多端点同时探测 (url1 & url2) |
| `trace` | 多模式并行扫描 (--pattern A & --pattern B) |
| `diff-logs` | 多对日志同时对比 (pair1 & pair2) |

**调度**：主会话 sessions_spawn 并行分发 → 各子会话独立超时 → 主会话汇总

## http 命令增强子模式

| 子模式 | 触发词 | 命令 |
|:------:|--------|------|
| SSL 深度检查 | ssl | `http --ssl <url>` |
| 重定向链 | redirect | `http --redirects <url>` |
| 各阶段耗时 | timing | `http --timing <url>` |
| 请求/响应头 | headers | `http --headers <url>` |