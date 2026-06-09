# self-improve.py — Auditor S5.9 Local Self-Improving Engine + Dual-Engine Dispatch
# Version: 2.1 | Fixed: yaml→json, Request POST, date format
# Reads: auditor audit results
# Updates: frozen_version.json + memory/auditor-patterns.json
# Dual-Engine: local self-improvement vs community capability-evolver

import json
import os
import re
from datetime import datetime
import urllib.request
import urllib.error

MEMORY_DIR = os.path.expanduser("~/.qclaw/workspace/memory")
SKILL_DIR = os.path.expanduser("~/.qclaw/skills/auditor")
PATTERNS_FILE = os.path.join(MEMORY_DIR, "auditor-patterns.json")
FROZEN_FILE = os.path.join(SKILL_DIR, "frozen_version.json")
CAPABILITY_EVOLVER_URL = "http://127.0.0.1:19820"


def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_patterns():
    return load_json(PATTERNS_FILE, {"patterns": [], "version": "1.0"})


def load_frozen():
    return load_json(FROZEN_FILE, {
        "consecutive_clean_audits": 0,
        "last_evolution": None,
        "frozen": False,
        "evolution_engines": {
            "self_improving": {"last_used": None, "patterns_added": 0},
            "capability_evolver": {"last_used": None, "genes_submitted": 0}
        }
    })


def now_date():
    """Return consistent date string."""
    return datetime.now().strftime('%Y-%m-%d')


def analyze_audit_results(audit_data):
    """Extract patterns from audit results for improvement."""
    issues = audit_data.get("issues_found", [])
    optimizations = audit_data.get("optimizations", [])
    layers_used = audit_data.get("layers_used", [])
    degraded = audit_data.get("degraded_layers", [])

    patterns = []
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Pattern: degraded layers → missing skills
    if degraded:
        patterns.append({
            "id": f"auditor_pattern_{ts}_dl",
            "source": "auditor_self_improvement",
            "confidence": 0.75,
            "applications": 1,
            "created": now_date(),
            "category": "degraded_layer",
            "pattern": f"Layers {degraded} were degraded — likely missing skills",
            "problem": f"Enhancement layers {degraded} unavailable",
            "solution": "Install missing skills before next audit",
            "quality_rules": [f"Install layer {l}" for l in degraded],
            "target_skills": ["auditor"]
        })

    # Pattern: repeated P0 issues
    p0_issues = [i for i in issues if i.get("priority") == "P0"]
    if len(p0_issues) >= 2:
        patterns.append({
            "id": f"auditor_p0_{ts}",
            "source": "auditor_self_improvement",
            "confidence": 0.85,
            "applications": 1,
            "created": now_date(),
            "category": "p0_repetition",
            "pattern": f"{len(p0_issues)} P0 issues found — system quality gates may be insufficient",
            "problem": "Multiple P0 issues in single audit",
            "solution": "Strengthen Q0-Q6 quality gates or add pre-audit checklist",
            "quality_rules": ["Review quality gate thresholds", "Add pre-audit Q0 check"],
            "target_skills": ["auditor"]
        })

    # Pattern: optimization opportunities
    for idx, opt in enumerate(optimizations):
        patterns.append({
            "id": f"auditor_opt_{ts}_{idx}",
            "source": "auditor_self_improvement",
            "confidence": 0.70,
            "applications": 1,
            "created": now_date(),
            "category": "optimization",
            "pattern": opt.get("description", ""),
            "problem": opt.get("problem", ""),
            "solution": opt.get("solution", ""),
            "quality_rules": opt.get("suggestions", []),
            "target_skills": ["auditor"]
        })

    return patterns


def check_repeated_patterns(patterns_db, new_patterns):
    """Check if any new patterns repeat existing ones ≥3 times."""
    repeated = []
    for new_p in new_patterns:
        category = new_p.get("category", "")
        similar = [p for p in patterns_db.get("patterns", []) if p.get("category") == category]
        if len(similar) >= 2:  # 2 existing + 1 new = 3 total
            repeated.append({
                "category": category,
                "count": len(similar) + 1,
                "pattern": new_p
            })
    return repeated


def submit_to_capability_evolver(pattern, frozen):
    """Submit pattern to capability-evolver community hub."""
    try:
        # Check if proxy is reachable
        search_data = json.dumps({
            "signals": ["auditor_optimization", pattern.get("category", "")],
            "mode": "semantic",
            "limit": 5
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{CAPABILITY_EVOLVER_URL}/asset/search",
            data=search_data,
            method="POST",
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            search_result = json.loads(resp.read().decode("utf-8"))

        # Submit as gene (use JSON instead of YAML to avoid dependency)
        gene_data = {
            "assets": [{
                "type": "Gene",
                "content": json.dumps({"patterns": {pattern["id"]: pattern}}, ensure_ascii=False, indent=2)
            }]
        }
        submit_data = json.dumps(gene_data).encode("utf-8")
        req2 = urllib.request.Request(
            f"{CAPABILITY_EVOLVER_URL}/asset/submit",
            data=submit_data,
            method="POST",
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req2, timeout=5) as resp2:
            submit_result = json.loads(resp2.read().decode("utf-8"))

        # Update frozen
        frozen["evolution_engines"]["capability_evolver"]["last_used"] = now_date()
        frozen["evolution_engines"]["capability_evolver"]["genes_submitted"] += 1
        return True, "Submitted to community hub"
    except Exception as e:
        return False, f"Hub offline, only local record: {str(e)}"


def update_frozen(frozen, patterns_added, genes_submitted=0):
    frozen["last_evolution"] = now_date()
    frozen["evolution_engines"]["self_improving"]["last_used"] = now_date()
    frozen["evolution_engines"]["self_improving"]["patterns_added"] += patterns_added
    if genes_submitted > 0:
        frozen["evolution_engines"]["capability_evolver"]["last_used"] = now_date()
        frozen["evolution_engines"]["capability_evolver"]["genes_submitted"] += genes_submitted
    return frozen


def main():
    import sys
    # Read audit data from stdin or file arg
    audit_data = {}
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            audit_data = json.load(f)
    else:
        try:
            audit_data = json.load(sys.stdin)
        except Exception:
            print("[self-improve] No audit data provided. Usage: python self-improve.py [audit-data.json]")
            sys.exit(1)

    patterns = analyze_audit_results(audit_data)

    if not patterns:
        print("[self-improve] No new patterns found, skipping update")
        sys.exit(0)

    # Update patterns file
    patterns_db = load_patterns()

    # Check for repeated patterns (S5.9 dual-engine dispatch)
    repeated = check_repeated_patterns(patterns_db, patterns)

    genes_submitted = 0
    for p in patterns:
        patterns_db["patterns"].append(p)

    save_json(PATTERNS_FILE, patterns_db)

    # Update frozen version
    frozen = load_frozen()

    # Dual-engine dispatch
    if repeated:
        for rep in repeated:
            if rep["count"] >= 3:
                success, msg = submit_to_capability_evolver(rep["pattern"], frozen)
                if success:
                    genes_submitted += 1
                    print(f"[self-improve] {msg}")
                else:
                    print(f"[self-improve] {msg}")

    frozen = update_frozen(frozen, len(patterns), genes_submitted)
    save_json(FROZEN_FILE, frozen)

    print(f"[self-improve] Added {len(patterns)} patterns to auditor-patterns.json")
    print(f"[self-improve] Updated frozen_version.json ({frozen['evolution_engines']['self_improving']['patterns_added']} total patterns)")
    if genes_submitted > 0:
        print(f"[self-improve] Submitted {genes_submitted} genes to community hub")


if __name__ == "__main__":
    main()
