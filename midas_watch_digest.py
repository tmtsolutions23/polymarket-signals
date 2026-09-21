#!/usr/bin/env python3
"""Midas daily watch digest (HERMES-009). Prints a compact status line per day.

Checks: scheduled runs healthy, failures/missed slots, scorecard recording +
resolution progress, pre-filter behavior, contract remaining days.
Quiet on nothing-new is NOT used here: a watch report posts daily by design.
"""
import json, os, sqlite3
from datetime import datetime, timezone, timedelta

DB = "/root/.n8n/.n8n/database.sqlite"
WORKFLOW = "4MqMruEVp1YutQf7"
HISTORY = "/root/polymarket-n8n/picks_history.jsonl"
STATE = os.path.expanduser("~/.hermes/scripts/.n8n_scanner_state.json")
SCORECARD_DIR = "/root/polymarket-n8n/scorecard"
EXPIRY = datetime(2026, 9, 25, tzinfo=timezone.utc)
NOW = datetime.now(timezone.utc)

lines = []
days_left = (EXPIRY - NOW).days + (1 if (EXPIRY - NOW).seconds > 0 else 0)
lines.append(f"**[MIDAS WATCH]** {NOW.strftime('%Y-%m-%d')} — contract: {max(days_left,0)}d left")

# --- runs in the last 26h ---
db = sqlite3.connect(DB)
rows = db.execute(
    "SELECT id, startedAt, stoppedAt, status, mode FROM execution_entity "
    "WHERE workflowId=? AND startedAt >= ? ORDER BY id",
    (WORKFLOW, (NOW - timedelta(hours=26)).strftime("%Y-%m-%d %H:%M:%S"))).fetchall()
if not rows:
    lines.append("⚠️ NO RUNS in the last 26h — pipeline silent!")
else:
    for r in rows:
        dur = ""
        if r[2]:
            try:
                s = datetime.fromisoformat(r[1]); e = datetime.fromisoformat(r[2])
                dur = f" ({int((e - s).total_seconds())}s)"
            except Exception:
                pass
        flag = "✅" if r[3] == "success" else "❌"
        lines.append(f"{flag} run #{r[0]} {r[4]} @ {r[1][:16]} — {r[3]}{dur}")
    trig = [r for r in rows if r[4] == "trigger" and r[3] == "success"]
    lines.append(f"Scheduled runs (24h): {len(trig)}/24 (hourly NY)")

# --- watcher state (alerts fired) ---
try:
    with open(STATE) as f:
        st = json.load(f)
    alerted = st.get("alerted") or []
    missed = st.get("missed") or []
    lines.append(f"Watcher: {len(alerted)} alerts, {len(missed)} missed slots")
except Exception:
    lines.append("Watcher state: unreadable")

# --- scorecard progress ---
try:
    n_run = n_pick = n_res = 0
    if os.path.exists(HISTORY):
        with open(HISTORY) as f:
            for ln in f:
                try:
                    o = json.loads(ln)
                except Exception:
                    continue
                if o.get("date") == NOW.strftime("%Y-%m-%d") or o.get("ts", "").startswith(NOW.strftime("%Y-%m-%d")):
                    if o.get("kind") == "run":
                        n_run += 1
                    elif o.get("kind") == "pick":
                        n_pick += 1
                        if (o.get("resolution") or {}).get("resolved"):
                            n_res += 1
    lines.append(f"Scorecard today: {n_run} runs, {n_pick} picks recorded, {n_res} resolved")
except Exception as e:
    lines.append(f"Scorecard check failed: {e}")

# --- latest scorecard summary ---
try:
    rep = os.path.join(SCORECARD_DIR, "reports", "latest-scorecard.md")
    if os.path.exists(rep):
        tail = [l.strip() for l in open(rep).read().splitlines() if l.strip()][-6:]
        lines.append("Scorecard (latest): " + " | ".join(tail[:4]))
except Exception:
    pass

print("\n".join(lines))
