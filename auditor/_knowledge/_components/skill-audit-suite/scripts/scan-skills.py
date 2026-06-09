#!/usr/bin/env python3
# scan-skills.py — Scan installed skills for auditor Layer A
import os
import json
import re
import sys

SKILLS_DIR = os.path.expanduser("~/.qclaw/skills")
OUTPUT = {"scanned": 0, "issues": [], "skills_ok": 0, "skills_with_issues": 0}

def scan_skill(skill_name):
    """Scan a single skill directory."""
    skill_path = os.path.join(SKILLS_DIR, skill_name)
    issues = []
    warnings = []

    if not os.path.isdir(skill_path):
        return None

    # 1. Check SKILL.md exists
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        issues.append({"type": "missing_skill_md", "severity": "P0", "msg": "SKILL.md not found"})
    else:
        # 2. Check skill has description
        content = open(skill_md, "r", encoding="utf-8", errors="ignore").read()
        if not re.search(r"description\s*[:=]", content):
            issues.append({"type": "missing_description", "severity": "P1", "msg": "SKILL.md missing description field"})

    # 3. Check for dangerous patterns
    if os.path.exists(skill_md):
        content = open(skill_md, "r", encoding="utf-8", errors="ignore").read()
        dangerous = [
            (r"rm\s+-rf\s+/\s", "DANGEROUS: rm -rf /"),
            (r"os\.system\s*\(\s*['\"].*sudo", "DANGEROUS: sudo via os.system"),
            (r"subprocess\.run\s*\(\s*\[.*-y\b", "DANGEROUS: unattended installs"),
            (r"open\s*\([^)]*['\"]\/etc\/", "POTENTIAL: writing to /etc"),
        ]
        for pattern, msg in dangerous:
            if re.search(pattern, content):
                issues.append({"type": "security", "severity": "P0", "msg": msg, "pattern": pattern})

    # 4. Check _hooks/ directory
    hooks_dir = os.path.join(skill_path, "_hooks")
    if os.path.isdir(hooks_dir):
        hook_files = os.listdir(hooks_dir)
        if hook_files:
            warnings.append({"type": "hooks_present", "msg": f"{len(hook_files)} hook(s): {', '.join(hook_files)}"})

    # 5. Check references/ directory
    refs_dir = os.path.join(skill_path, "references")
    if not os.path.isdir(refs_dir):
        warnings.append({"type": "no_references", "msg": "No references/ directory"})

    return {
        "skill": skill_name,
        "path": skill_path,
        "issues": issues,
        "warnings": warnings,
        "status": "fail" if any(i["severity"] == "P0" for i in issues) else "warn" if issues else "ok"
    }

def main():
    json_output = "--json" in sys.argv
    all_skills = os.path.exists(SKILLS_DIR)
    target = None

    for arg in sys.argv[1:]:
        if arg in ("--all", "--json"):
            continue
        if arg.startswith("--skill=") or arg.startswith("--skill"):
            target = arg.split("=")[-1]

    if target:
        result = scan_skill(target)
        if result:
            OUTPUT["scanned"] = 1
            OUTPUT["issues"].append(result)
            if result["status"] == "ok":
                OUTPUT["skills_ok"] = 1
            else:
                OUTPUT["skills_with_issues"] = 1
    elif all_skills:
        for skill_name in os.listdir(SKILLS_DIR):
            if skill_name.startswith("."):
                continue
            result = scan_skill(skill_name)
            if result:
                OUTPUT["scanned"] += 1
                if result["status"] == "ok":
                    OUTPUT["skills_ok"] += 1
                else:
                    OUTPUT["skills_with_issues"] += 1
                if result["issues"] or result["warnings"]:
                    OUTPUT["issues"].append(result)

    if json_output:
        print(json.dumps(OUTPUT, indent=2, ensure_ascii=False))
    else:
        print(f"[scan-skills] Scanned: {OUTPUT['scanned']} | OK: {OUTPUT['skills_ok']} | Issues: {OUTPUT['skills_with_issues']}")
        for s in OUTPUT["issues"]:
            if s["issues"]:
                print(f"\n  ⚠️  {s['skill']}:")
                for i in s["issues"]:
                    print(f"    [{i['severity']}] {i['msg']}")
            if s["warnings"]:
                for w in s["warnings"]:
                    print(f"    [warn] {w['msg']}")

    sys.exit(0 if OUTPUT["skills_with_issues"] == 0 else 1)

if __name__ == "__main__":
    main()