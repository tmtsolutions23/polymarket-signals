# Polymarket Scanner — Rollup

Shareable status ("what updates the company"). Maintained by DRI (Atlas).

## Status: LIVE — folded into org (2026-09-17); hourly cadence + change gate (2026-09-18, HERMES-010)

The Polymarket Smart Money Consensus pipeline is a company project (HERMES-002, D-005). Report-only copy signals, now **hourly NY** (cron `0 * * * *`) posting **only on new/changed signals** — no filler (HERMES-010 change gate). Ownership: Atlas (COO) as DRI; CEO approves any deploy/change to the live pipeline (guarded).

## This week

- Folded into org; brief + runbook + change control live in this folder.
- Iteration backlog opened: HERMES-003 (scorecard, P1) · HERMES-004 (cadence audit — resolved by tz change) · HERMES-005 (failure alerting, P2) · HERMES-006 (secrets hygiene, P3).
- Formal C-suite review delivered (HERMES-007): verdict healthy; new finding F3 → HERMES-008 (stale settle-date verification, P1). Full review: `Review-CSuite-2026-09-17.md`.
- HERMES-005 done: failure watcher live (cron every 5 min) — failed runs alert to #polymarket-daily (fallback #blockers), missed-slot detection, standup digest now carries run-health line. Induced failure tested end-to-end.
- HERMES-008 done (bundle v2, CEO-approved): settle-gate fix + ≥$10k noise pre-filter deployed & live-tested; workflow renamed "07:00+18:00 NY". Bankroll → $96.75 (Sonmez stake taken).
- HERMES-010 done (2026-09-18, CEO-approved): hourly scan (cron `0 * * * *`) + change-detection gate (posts only new/changed signals vs `last_posted.json`; fail-open; 90-min re-post gap; silent no-signal path). Unit-tested (post/silent/new) + live webhook runs 37/38 success. No-picks filler posts removed.

## Metrics (pipeline)

- Runs/day: 24 (hourly NY); posts only on new/changed signals (HERMES-010 change gate)
- Picks → outcome tracking: LIVE (HERMES-003) — `picks_history.jsonl` + gamma resolution + weekly scorecard
- Error alerting: LIVE since 2026-09-17 (HERMES-005) — alert-to-post latency ≤5 min, deduped per execution/slot

## Blocked / risks

- HERMES-006 (secrets hygiene) queued — needs guarded deploy.
- **Signal-quality flag (scorecard interim):** 0/1 COPY won; 3/3 settled SKIPs won. Either the gates are too strict or early noise — official weekly scorecard (≥7 rated days, ~Sep 24) decides. CEO's bottom-line mandate means gate tuning is the priority once data is in.

## Scorecard

Tracker live (HERMES-003): 28 scheduled runs, 23 rated picks recorded → `picks_history.jsonl`.
Status: **INTERIM** — 4 scheduled-rated days (gate ≥7); official weekly auto-fires when the gate is met (cron daily).
- COPY: 3 picks, 0/2 settled won → 0.0%
- WATCH→winner: 1/1 settled won
- SKIP false-negative: 11/12 settled SKIPs won anyway → 91.7%
- Latest report: `scorecard/reports/latest-scorecard.md` (2026-09-20 23:05 UTC)
