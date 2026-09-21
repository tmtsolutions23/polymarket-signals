---
id: HERMES-005
title: Failure alerting for scanner runs
requester: Atlas (via HERMES-002 fold-in)
dri: Atlas
team: C-Suite (Operations)
priority: P2
status: Done
created: 2026-09-17
due: none
acceptance_criteria:
  - Failed run → visible Discord alert within 15 min (tested)
  - No false alerts on success
  - Standup digest includes run-health line
  - Documented in Brief (risks) + Rollup
dependencies: none (HERMES-002 parent done)
delegation_chain: CEO → Atlas
links:
  vault_note: 20-Projects/Polymarket-Scanner/HERMES-005.md
  kanban_card: t_0632ebe9
  thread: none
---

# HERMES-005 — Failure alerting for scanner runs

## Why

Workflow error paths are silent — a missed signal day goes unnoticed.

## Spec (summary)

Host-side watcher (Option B — no n8n deploy, D-005-safe): checks the local n8n
execution DB every 5 min for failed runs of workflow `4MqMruEVp1YutQf7` and
posts one alert per failure to **#polymarket-daily** via the pipeline's own
webhook; falls back to **#blockers** if that webhook is dead. Detects missed
scheduled slots too. Run-health folded into the Atlas standup digest.

## What was built

- `~/.hermes/scripts/n8n_failure_watcher.py` — watcher (stdlib only):
  - **Failed runs:** statuses `error|failed|crashed` within a 6 h lookback,
    one alert per execution id (dedup via state file
    `~/.hermes/scripts/.n8n_scanner_state.json`, chmod 600). Error message
    extracted from `execution_data` (n8n indexed-array pointer traversal,
    incl. pointer-typed message values).
  - **Missed slots:** cron expression + instance tz
    (`N8N_DEFAULT_TIMEZONE=America/New_York`) read live from the DB/env;
    a slot >60 min past its start with no execution in
    `[start−10m, start+60m]` triggers a "no run detected" alert, deduped per
    slot. False-positive guards: slot must have run before (same local time,
    previous day) AND a trigger-mode run must exist within the prior 30 h —
    this correctly ignored the Sep-15 18:00 NY slot (cron was `0 7 * * *`
    until 2026-09-16 04:56 UTC; verified via `workflow_history`).
  - **Webhook:** extracted live from the workflow definition (rotated
    webhooks are picked up automatically); fallback to `#blockers` webhook
    (added to `webhooks.json`).
  - **Health snapshot** written every tick for the standup digest
    (last execution, failures/24 h, last failure, missed slots).
- `~/.hermes/scripts/standup_digest.py` — now includes a **Scanner health**
  line; state is written AFTER a successful post (fixes the old
  write-before-post silent-watchdog trap); `--no-post` for dry runs.
- Cron `353e5ceabcbd` — `*/5 * * * *`, no_agent, deliver=local (script posts
  to Discord itself).
- `#blockers` persona webhook added to `webhooks.json` (8 channels now).

## Test evidence (2026-09-17)

- **Induced failure:** `POST /webhook/poly-consensus` without the guard key →
  execution #27 errored ("Unauthorized: missing/invalid x-consensus-key
  header") → watcher posted the alert to #polymarket-daily at 04:32:27 UTC
  (verified via Discord API; clarifying note posted at 04:35:46 UTC).
- **No false alerts:** immediate re-run stayed quiet (no duplicate); all
  successful runs (execs 25/26 etc.) never alert.
- **Real historical failure:** exec #20 (Sep 16, "Identifier 'hoursAgo' has
  already been declared") correctly detected + message extracted (dry-run).
- **Schedule-change gate:** simulated Sep-15 18:00 NY slot → NOT flagged
  (cron changed 2026-09-16); simulated genuine misses (Sep-17 slots) → flagged.
- **Fallback:** forced pipeline-webhook failure → alert landed in #blockers
  as Atlas (verified via Discord API).
- **Standup line:** `standup_digest.py --no-post` renders the Scanner health
  line with the last failure + counts.
- Test execution #27 removed from the DB afterwards (DB clean).

## Log

- 2026-09-17: ticket created as part of HERMES-002 fold-in.
- 2026-09-17: implemented (Option B watcher + standup integration), induced
  failure tested end-to-end, cron `353e5ceabcbd` live, docs updated.

## Result

All acceptance criteria met: failed runs alert to #polymarket-daily within
≤5 min (tested with an induced failure, observed via Discord API); successful
runs produce no alerts; the Atlas standup digest now carries a run-health
line; risk documented in Brief + Rollup. Missed-slot detection (no execution
at all for a scheduled slot — e.g. n8n down) is included as a bonus: one
alert per missed slot, gated to avoid schedule-change false positives.
