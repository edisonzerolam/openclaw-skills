/**
 * debug-core.js — Cross-platform system debugging (Node.js)
 * Commands: trace | stacktrace | leaks | profile | diff-logs | http | parallel
 * Output: JSON {status, summary, details}
 */
const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const http = require('http');
const https = require('https');

const isWindows = process.platform === 'win32' || process.env.OSTYPE === 'msys';
const isMac = process.platform === 'darwin';
const isLinux = process.platform === 'linux';

function exec(cmd, opts = {}) {
  try {
    return execSync(cmd, { encoding: 'utf8', stdio: 'pipe', ...opts });
  } catch (e) {
    return e.stdout || '';
  }
}

// === trace: find error patterns in log files ===
function cmdTrace(args) {
  let pattern = args.pattern || 'ERROR|FATAL|Exception|Traceback|WARN|OOM|Segfault|panic|SIGKILL|SIGSEGV';
  let file = args.file || args._[0];
  let timeFilter = null;

  if (!file) return { status: 'error', summary: 'Usage: debug trace [--pattern REGEX] [--last 1h|30m|2d] <logfile>' };
  if (!fs.existsSync(file)) return { status: 'error', summary: `File not found: ${file}` };

  const content = fs.readFileSync(file, 'utf8');
  const lines = content.split('\n');
  const totalLines = lines.length;

  if (args.last) {
    const now = Date.now();
    let ms;
    if (args.last.endsWith('h')) ms = parseInt(args.last) * 3600000;
    else if (args.last.endsWith('m')) ms = parseInt(args.last) * 60000;
    else if (args.last.endsWith('d')) ms = parseInt(args.last) * 86400000;
    else ms = 0;
    const cutoff = new Date(now - ms).toISOString().replace(/T/, ' ').substring(0, 19);
    timeFilter = cutoff;
  }

  const errorTypes = ['ERROR', 'FATAL', 'Exception', 'Traceback', 'WARN', 'OOM', 'Segfault', 'panic'];
  const matches = lines.filter(line => {
    if (timeFilter && line < timeFilter) return false;
    return errorTypes.some(t => line.includes(t));
  });

  const breakdown = {};
  errorTypes.forEach(t => {
    const count = matches.filter(l => l.includes(t)).length;
    if (count > 0) breakdown[t] = count;
  });

  const normalized = matches.map(l =>
    l.replace(/[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}:[0-9]{2}[^ ]*/g, 'TS')
     .replace(/0x[0-9a-fA-F]+/g, '0xA')
     .replace(/pid=[0-9]*/g, 'pid=N')
  );
  const uniquePatterns = {};
  normalized.forEach(l => {
    if (uniquePatterns[l]) uniquePatterns[l]++;
    else uniquePatterns[l] = 1;
  });
  const topPatterns = Object.entries(uniquePatterns)
    .sort((a, b) => b[1] - a[1]).slice(0, 10)
    .map(([p, c]) => ({ pattern: p, count: c }));

  return {
    status: matches.length > 0 ? 'errors' : 'clean',
    errors_found: matches.length,
    total_lines: totalLines,
    breakdown,
    last_20: matches.slice(-20),
    unique_patterns: topPatterns,
    summary: `Found ${matches.length} matches in ${totalLines} lines`
  };
}

// === stacktrace: parse and summarize a stack trace ===
function cmdStacktrace(input) {
  let content = input;
  if (input === '-' || !input) {
    content = '';
  } else if (fs.existsSync(input)) {
    content = fs.readFileSync(input, 'utf8');
  }
  if (!content) return { status: 'error', summary: 'Usage: debug stacktrace <file|->' };

  let lang = 'unknown';
  if (content.includes('Traceback (most recent call last)')) lang = 'python';
  else if (content.includes('at .*(.*.java:')) lang = 'java';
  else if (content.includes('at .*(.*.js:')) lang = 'javascript';
  else if (content.includes('goroutine ')) lang = 'go';
  else if (content.includes('thread ') && content.includes('#')) lang = 'c_cpp';

  const errorLines = content.split('\n').filter(l => l.trim() && !l.startsWith('  '));
  const errorMessage = errorLines[errorLines.length - 1] || content.split('\n')[0];
  const frameMatches = content.match(/^\s*(at |File ")/gm) || [];

  return {
    status: 'ok',
    language: lang,
    error_message: errorMessage,
    stack_depth: frameMatches.length,
    raw_snippet: content.substring(0, 1000)
  };
}

// === leaks: monitor process memory over time ===
function cmdLeaks(args) {
  const pid = parseInt(args.pid || args._[0]);
  const duration = parseInt(args.duration || 30);
  const interval = parseInt(args.interval || 5);
  if (!pid || isNaN(pid)) return { status: 'error', summary: 'Usage: debug leaks --pid <PID> [--duration N] [--interval N]' };

  const samples = [];
  for (let elapsed = 0; elapsed < duration; elapsed += interval) {
    let rss = 0, vsz = 0;
    try {
      if (isWindows) {
        const out = exec(`wmic.exe process where "processid=${pid}" get WorkingSetSize /value`, { windowsHide: true });
        const match = out.match(/WorkingSetSize=([0-9]+)/i);
        if (match) rss = Math.round(parseInt(match[1]) / 1024);
      } else {
        const out = exec(`ps -p ${pid} -o rss=,vsz= 2>/dev/null`);
        const parts = out.trim().split(/\s+/);
        rss = parseInt(parts[0]) || 0;
        vsz = parseInt(parts[1]) || 0;
      }
    } catch { return { status: 'error', summary: `Process ${pid} not found` }; }

    const delta = samples.length > 0 ? rss - samples[samples.length - 1].rss : 0;
    samples.push({ elapsed, rss, vsz, delta });
    if (elapsed + interval < duration) {
      const start = Date.now();
      while (Date.now() - start < interval * 1000) {}
    }
  }

  const first = samples[0].rss, last = samples[samples.length - 1].rss;
  const growth = last - first;
  const growthPct = first > 0 ? Math.round(growth * 100 / first) : 0;

  return {
    status: growthPct > 20 ? 'possible_leak' : 'ok',
    pid, duration, interval,
    samples,
    summary: { start_rss_kb: first, end_rss_kb: last, growth_kb: growth, growth_pct: growthPct },
    verdict: growthPct > 20 ? `POSSIBLE LEAK: Memory grew ${growthPct}%` : `OK: Memory stable (${growthPct}% change)`
  };
}

// === profile: measure execution time ===
function cmdProfile(args) {
  const repeat = parseInt(args.repeat || 1);
  const cmd = args.command || args._.join(' ') || (args._.length > 1 ? args._.slice(1).join(' ') : '');
  if (!cmd) return { status: 'error', summary: 'Usage: debug profile [--repeat N] <command>' };

  const results = [];
  for (let run = 1; run <= repeat; run++) {
    const start = Date.now();
    let exitCode = 0;
    try { exec(cmd, { stdio: 'ignore' }); } catch (e) { exitCode = e.status || 1; }
    results.push({ run, elapsed_ms: Date.now() - start, exit: exitCode });
  }
  const times = results.map(r => r.elapsed_ms);
  return {
    status: Math.max(...times) > 5000 ? 'slow' : Math.max(...times) > 1000 ? 'moderate' : 'fast',
    command: cmd, runs: repeat, results,
    summary: { avg_ms: Math.round(times.reduce((a, b) => a + b, 0) / times.length), min_ms: Math.min(...times), max_ms: Math.max(...times) },
    verdict: Math.max(...times) > 5000 ? 'SLOW: Over 5 seconds' : Math.max(...times) > 1000 ? 'MODERATE: Over 1 second' : 'FAST: Under 1 second'
  };
}

// === diff-logs: compare two log files ===
function cmdDiffLogs(args) {
  const [file1, file2] = [args._[0], args._[1]];
  if (!file1 || !file2) return { status: 'error', summary: 'Usage: debug diff-logs [--errors-only] <file1> <file2>' };
  if (!fs.existsSync(file1) || !fs.existsSync(file2)) return { status: 'error', summary: 'Files not found' };

  const lines1 = fs.readFileSync(file1, 'utf8').split('\n');
  const lines2 = fs.readFileSync(file2, 'utf8').split('\n');
  const errPattern = /ERROR|FATAL|Exception|Traceback|WARN/gi;
  const set1 = new Set(lines1.filter(l => errPattern.test(l)));
  const set2 = new Set(lines2.filter(l => errPattern.test(l)));
  const newErrors = [...set2].filter(l => !set1.has(l));
  const removed = [...set1].filter(l => !set2.has(l));

  return {
    status: newErrors.length > 0 ? 'new_errors' : 'clean',
    line_counts: { [file1]: lines1.length, [file2]: lines2.length, diff: lines2.length - lines1.length },
    error_counts: { [file1]: set1.size, [file2]: set2.size, diff: set2.size - set1.size },
    new_errors: newErrors.slice(0, 20),
    removed_errors: removed.slice(0, 20),
    summary: `${newErrors.length} new errors, ${removed.length} removed`
  };
}

// === http: debug HTTP requests ===
function cmdHttp(args) {
  const url = args._[0] || args.url;
  if (!url) return { status: 'error', summary: 'Usage: debug http [--verbose] [--timing] <url>' };

  try {
    const curlCmd = `curl -s -o /dev/null -w "%{http_code}|%{time_total}|%{size_download}" "${url}"`;
    const curlOut = exec(curlCmd);
    const [code, time, size] = (curlOut || '000|0|0').split('|');
    return {
      status: parseInt(code) >= 400 ? 'error' : 'ok',
      status_code: parseInt(code) || 0,
      timing: { total_ms: Math.round(parseFloat(time || 0) * 1000), size_bytes: parseInt(size || 0) },
      summary: `Status ${code || '000'}, ${size || 0} bytes in ${Math.round(parseFloat(time || 0) * 1000)}ms`
    };
  } catch (e) {
    return { status: 'error', summary: `Failed to fetch ${url}` };
  }
}

// === parallel: E6 multi-source parallel reading ===
async function fetchUrl(url, timeout = 30000) {
  const client = url.startsWith('https') ? https : http;
  return new Promise(resolve => {
    const start = Date.now();
    const req = client.get(url, { headers: { 'User-Agent': 'QClaw-Debug/1.0' }, timeout }, res => {
      let body = '';
      res.on('data', d => { body += d; });
      res.on('end', () => resolve({
        url, status: 'ok', statusCode: res.statusCode,
        elapsed_ms: Date.now() - start,
        size_bytes: Buffer.byteLength(body),
        snippet: body.substring(0, 200)
      }));
    });
    req.on('error', e => resolve({ url, status: 'error', error: e.message, elapsed_ms: Date.now() - start }));
    req.on('timeout', () => { req.destroy(); resolve({ url, status: 'timeout', elapsed_ms: timeout }); });
    setTimeout(() => { if (!req.destroyed) req.destroy(); }, timeout);
  });
}

async function invokeParallel(sources = [], maxConcurrency = 3) {
  const results = [];
  for (let i = 0; i < sources.length; i += maxConcurrency) {
    const batch = sources.slice(i, i + maxConcurrency);
    const batchResults = await Promise.all(batch.map(url => fetchUrl(url)));
    results.push(...batchResults);
  }
  const ok = results.filter(r => r.status === 'ok').length;
  const errs = results.filter(r => r.status !== 'ok').length;
  return {
    level: 'E6', sources_total: sources.length, sources_ok: ok, sources_error: errs,
    findings: results.map(r => ({ source: r.url, status: r.status, key_data: r.snippet || '', anomaly: r.status !== 'ok' ? `${r.status}: ${r.error || ''}` : null })),
    report_summary: `${ok} OK, ${errs} error/timeout`
  };
}

// === Main dispatcher ===
async function main() {
  const [cmd, ...restArgs] = process.argv.slice(2);
  const args = { _: [] };

  for (let i = 0; i < restArgs.length; i++) {
    const a = restArgs[i];
    if (a.startsWith('--')) {
      const key = a.replace('--', '');
      if (key === 'verbose' || key === 'timing' || key === 'errors-only') {
        args[key] = true;
      } else if (restArgs[i + 1] !== undefined && !restArgs[i + 1].startsWith('--')) {
        args[key] = restArgs[i + 1];
        i++;
      } else {
        args[key] = true;
      }
    } else {
      args._.push(a);
    }
  }

  let result;
  switch (cmd) {
    case 'trace': result = cmdTrace(args); break;
    case 'stacktrace': result = cmdStacktrace(restArgs[0] || '-'); break;
    case 'leaks': result = cmdLeaks(args); break;
    case 'profile': result = cmdProfile(args); break;
    case 'diff-logs': result = cmdDiffLogs(args); break;
    case 'http': result = cmdHttp(args); break;
    case 'parallel': result = await invokeParallel(args._); break;
    default:
      result = { summary: `debug v1.0 — Commands: trace | stacktrace | leaks | profile | diff-logs | http | parallel` };
  }

  console.log(JSON.stringify(result, null, 2));
  process.exit(result.status === 'error' ? 1 : 0);
}

if (require.main === module) main();
module.exports = { cmdTrace, cmdStacktrace, cmdLeaks, cmdProfile, cmdDiffLogs, cmdHttp, invokeParallel, fetchUrl };