# residual-generator.py — Generate Cron Reminders from Plan Tracker Files
# Version: 1.0 | For agent-planner T5 + auditor S5 residual tracking
# Reads: {workspace}/plan-tracker/{plan-id}.json
# Outputs: Cron job JSON payloads

import json
import os
import sys
from datetime import datetime, timedelta

WORKSPACE = os.path.join(os.path.expanduser("~"), ".qclaw", "workspace", "plan-tracker")
TRACKER_VERSION = "1.0"
DAYS_THRESHOLD = 7  # <7 days = at, >=7 days = cron

def load_tracker(plan_id):
    filepath = os.path.join(WORKSPACE, f"{plan_id}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_cron_payloads(tracker):
    """Generate cron payloads for all pending changes."""
    payloads = []
    now = datetime.now()

    for version in tracker.get("versions", []):
        for change in version.get("changes", []):
            if change.get("status") != "pending":
                continue

            chg_id = change.get("id", "unknown")
            desc = change.get("description", "")
            chg_type = change.get("type", "other")
            target = change.get("target", "")
            priority = change.get("priority", "P1")
            due_at = change.get("dueAt")

            # Determine schedule
            if due_at:
                due_dt = datetime.fromisoformat(due_at.replace("Z", "+00:00").replace("+08:00", ""))
                delta = (due_dt - now).days
                if delta < 0:
                    # Overdue — generate immediate one-shot
                    schedule_kind = "at"
                    schedule_at = now.isoformat()
                elif delta < DAYS_THRESHOLD:
                    # < 7 days — one-shot at due date
                    schedule_kind = "at"
                    schedule_at = due_dt.isoformat()
                else:
                    # >= 7 days — daily cron at 09:00
                    schedule_kind = "cron"
                    schedule_expr = "0 9 * * *"
            else:
                # No due date — one-shot 24h from now
                schedule_kind = "at"
                schedule_at = (now + timedelta(hours=24)).isoformat()
                schedule_expr = None

            plan_name = tracker.get("planName", "unknown-plan")
            name = f"[PlanTrack] {plan_name} #{chg_id}"

            # Build payload
            payload = {
                "name": name,
                "schedule": {
                    "kind": schedule_kind,
                    "at": schedule_at
                } if schedule_kind == "at" else {
                    "kind": "cron",
                    "expr": schedule_expr or "0 9 * * *",
                    "tz": "Asia/Shanghai"
                },
                "payload": {
                    "kind": "agentTurn",
                    "message": f"""【规划执行提醒：{plan_name} #{chg_id}】

请检查规划变更是否已实施。

读取 plan-tracker/{tracker.get("planId", plan_id)}.json

在 changes[] 中找到 id="{chg_id}"：
- 如果 status="applied"：静默结束
- 如果 status="pending"：提醒用户尽快实施

变更详情：
- 描述：{desc}
- 类型：{chg_type}
- 目标：{target}
- 优先级：{priority}
""",
                    "timeoutSeconds": 60
                },
                "delivery": {
                    "mode": "announce",
                    "bestEffort": True
                },
                "enabled": True,
                "deleteAfterRun": schedule_kind == "at"
            }

            payloads.append(payload)

    return payloads

def main():
    if len(sys.argv) < 2:
        # Auto-detect: find all tracker files with pending changes
        print("[residual-generator] Scanning plan-tracker/ for pending changes...")
        pending = []
        if os.path.exists(WORKSPACE):
            for fname in os.listdir(WORKSPACE):
                if not fname.endswith(".json"):
                    continue
                with open(os.path.join(WORKSPACE, fname), "r", encoding="utf-8") as f:
                    tracker = json.load(f)
                for version in tracker.get("versions", []):
                    for change in version.get("changes", []):
                        if change.get("status") == "pending":
                            pending.append(tracker.get("planId", fname[:-5]))
                            break
        if pending:
            print(f"[residual-generator] Found {len(pending)} plans with pending changes")
            for p in pending:
                print(f"  - {p}")
            print("[residual-generator] Pass plan-id as argument to generate crons")
        else:
            print("[residual-generator] No pending changes found")
        return

    plan_id = sys.argv[1]
    tracker = load_tracker(plan_id)
    if not tracker:
        print(f"[residual-generator] Tracker not found: {plan_id}")
        sys.exit(1)

    payloads = generate_cron_payloads(tracker)
    print(f"[residual-generator] Generated {len(payloads)} cron jobs for {plan_id}")
    print(json.dumps(payloads, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()