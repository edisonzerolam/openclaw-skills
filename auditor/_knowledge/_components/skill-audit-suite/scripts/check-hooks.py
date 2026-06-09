#!/usr/bin/env python3
# check-hooks.py — Check if a skill has audit hooks ready (for CI/CD)
import os
import sys

SKILLS_DIR = os.path.expanduser("~/.qclaw/skills")

VALID_HOOKS = ["pre-audit", "post-audit", "on-change", "pre-deploy"]

def check_hooks(skill_name):
    hooks_dir = os.path.join(SKILLS_DIR, skill_name, "_hooks")
    if not os.path.isdir(hooks_dir):
        return {"skill": skill_name, "status": "no_hooks", "hooks": [], "ready": False}

    hooks = os.listdir(hooks_dir)
    valid = [h for h in hooks if h in VALID_HOOKS]
    return {
        "skill": skill_name,
        "status": "ok",
        "hooks": hooks,
        "valid_hooks": valid,
        "ready": len(valid) > 0
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: check-hooks.py <skill-name>")
        sys.exit(1)

    result = check_hooks(sys.argv[1])
    print(f"[check-hooks] {result['skill']}: {result['status']}")
    if result.get("hooks"):
        print(f"  Hooks: {', '.join(result['hooks'])}")
        print(f"  Valid: {', '.join(result.get('valid_hooks', []))}")
    sys.exit(0 if result["ready"] else 1)