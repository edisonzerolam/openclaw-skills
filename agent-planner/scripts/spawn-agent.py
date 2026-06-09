#!/usr/bin/env python3
# spawn-agent.py v3.2 — Use short 8.3 path for ps1 file (no Chinese chars)
import subprocess, sys, json, os, tempfile, time

def run_openclaw(args, timeout=30):
    # Use short path for ps1 (no Chinese chars in path)
    # Get short 8.3 path for TEMP
    tmp_long = os.path.join(tempfile.gettempdir(), f"oa_out_{os.getpid()}.json")
    flag_long = os.path.join(tempfile.gettempdir(), f"oa_done_{os.getpid()}.flag")
    
    # Get short path names to avoid Chinese character issues
    import subprocess
    try:
        tmp_short = subprocess.run(
            ['cmd', '/c', 'for %A in ("' + tempfile.gettempdir() + '") do @echo %~sA'],
            capture_output=True, text=True, timeout=5
        ).stdout.strip()
        tmp = os.path.join(tmp_short, f"oa_out_{os.getpid()}.json")
        flag = os.path.join(tmp_short, f"oa_done_{os.getpid()}.flag")
        ps1_dir = tmp_short
    except:
        tmp = tmp_long
        flag = flag_long
        ps1_dir = tempfile.gettempdir()
    
    ps1 = os.path.join(ps1_dir, f"oa_ps_{os.getpid()}.ps1")
    
    # Build script with individual args
    arg_defs = "\n".join(f"$arg{i} = \"{a.replace('\"', '`\"')}\"" for i, a in enumerate(args))
    arg_list = ",".join(f"$arg{i}" for i in range(len(args)))
    
    ps_script = f"""
$outFile = "{tmp.replace(chr(92), '\\\\')}"
$flagFile = "{flag.replace(chr(92), '\\\\')}"
{arg_defs}
$argList = @({arg_list})
$proc = Start-Process -FilePath 'openclaw' -ArgumentList $argList -NoNewWindow -Wait -PassThru -RedirectStandardOutput $outFile
if ($proc.ExitCode -eq 0) {{ "done" | Out-File -FilePath $flagFile }} else {{ "fail:$($proc.ExitCode)" | Out-File -FilePath $flagFile }}
"""
    
    with open(ps1, "w", encoding="utf-8-sig") as f:
        f.write(ps_script)
    
    try:
        start_time = time.time()
        cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -File "{ps1}"'
        r = subprocess.run(cmd, capture_output=True, timeout=timeout, shell=True)
        elapsed = time.time() - start_time
        
        content = ""
        if os.path.exists(tmp):
            try:
                with open(tmp, "rb") as f:
                    raw = f.read()
                content = raw.decode("utf-8", errors="replace")
                json_start = content.find("{")
                if json_start > 0:
                    content = content[json_start:]
            except:
                content = ""
        
        return {"rc": r.returncode, "stdout": content, "elapsed": elapsed}
    finally:
        for f in [ps1, tmp, flag]:
            try: os.remove(f)
            except: pass

def invoke_L3(task, agent_id="main"):
    args = ["agent", "--agent", agent_id, "--message", task, "--json"]
    r = run_openclaw(args, timeout=25)
    try:
        parsed = json.loads(r["stdout"])
        text = (parsed.get("result", {}).get("payloads", [{}])[0].get("text", "") or
               parsed.get("result", {}).get("finalAssistantVisibleText", "")) if parsed.get("result") else ""
        return {"level": "L3", "speedup": "1x", "status": "ok", "output": text,
                "elapsed_s": round(r.get("elapsed", 0), 1)}
    except json.JSONDecodeError:
        return {"level": "L3", "status": "error", "output": r["stdout"][:500],
                "elapsed_s": round(r.get("elapsed", 0), 1)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"v": "3.2", "usage": "L3 <task> [agentId]"}))
        sys.exit(0)
    cmd, task = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "hello"
    result = invoke_L3(task, sys.argv[3] if len(sys.argv) > 3 else "main")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("status") == "ok" else 1)