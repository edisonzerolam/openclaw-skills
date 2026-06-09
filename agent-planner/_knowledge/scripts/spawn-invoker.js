#!/usr/bin/env node
/**
 * spawn-invoker.js v1.7 — Simple cmd /c approach (inline, no temp PS1)
 * Uses: cmd /c "openclaw ... > %TEMP%\out.txt" pattern
 */
const { spawn, execSync } = require('child_process');
const fs = require('fs');
const os = require('os');

const DEFAULT_AGENT = 'main';
const path = require('path');
const OUT = path.join(os.tmpdir(), 'sp_out.txt');

function runCmd(cmdStr, timeoutMs = 30000) {
    return new Promise((resolve) => {
        try { fs.unlinkSync(OUT); } catch {}
        fs.writeFileSync(OUT, '', 'utf8');

        const proc = spawn('cmd', ['/c', cmdStr], {
            stdio: 'ignore',
            shell: false,
            windowsHide: true,
            cwd: os.homedir()
        });

        const timer = setTimeout(() => {
            try { proc.kill(); } catch {}
            resolve({ code: -1, stdout: '', stderr: 'timeout' });
        }, timeoutMs);

        proc.on('close', (code) => {
            clearTimeout(timer);
            let stdout = '';
            try { stdout = fs.readFileSync(OUT, 'utf8'); } catch {}
            try { fs.unlinkSync(OUT); } catch {}
            resolve({ code: code || 0, stdout, stderr: '' });
        });

        proc.on('error', (e) => {
            clearTimeout(timer);
            resolve({ code: -1, stdout: '', stderr: e.message });
        });
    });
}

async function invokeL3(task, agentId = DEFAULT_AGENT) {
    // Build the command inline: redirect stdout to file
    const openclawCmd = `openclaw agent --agent ${agentId} --message "${task.replace(/"/g, '""')}" --json`;
    // cmd /c redirect: stdout > %TEMP%\sp_out.txt
    const cmdStr = `${openclawCmd} > "${OUT.replace(/\\/g, '\\\\')}" 2>&1`;

    const r = await runCmd(cmdStr, 35000);
    if (r.code === -1) return { level: 'L3', status: 'timeout' };

    try {
        const p = JSON.parse(r.stdout);
        const text = p.result?.payloads?.[0]?.text || p.result?.finalAssistantVisibleText || '';
        return { level: 'L3', speedup: '1x', status: 'ok', output: text.substring(0, 200) };
    } catch {
        return { level: 'L3', speedup: '1x', status: 'ok', output: r.stdout.substring(0, 200) };
    }
}

async function invokeL2(task, agentIds = [DEFAULT_AGENT]) {
    const results = await Promise.all(agentIds.map(id => invokeL3(task, id)));
    const ok = results.filter(r => r.status === 'ok').length;
    return { level: 'L2', speedup: `${agentIds.length}x`, status: ok === results.length ? 'ok' : 'partial', results };
}

async function main() {
    const [, , cmd, ...rest] = process.argv;
    let result;
    switch (cmd) {
        case 'L3': result = await invokeL3(rest[0] || 'hi', rest[1] || DEFAULT_AGENT); break;
        case 'L2': result = await invokeL2(rest[0] || 'hi', rest.slice(1).length ? rest.slice(1) : [DEFAULT_AGENT]); break;
        default: result = { summary: 'spawn-invoker.js v1.7' };
    }
    console.log(JSON.stringify(result, null, 2));
    process.exit(result.status === 'error' ? 1 : 0);
}

if (require.main === module) main();
module.exports = { invokeL3, invokeL2 };