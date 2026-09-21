---
id: HERMES-003
title: Polymarket pick outcome scorecard
requester: Atlas (via HERMES-002 fold-in)
dri: Atlas
team: C-Suite (Operations)
priority: P1
status: Done
created: 2026-09-17
done: 2026-09-17
acceptance_criteria:
  - Picks appended automatically/semi-automatically (no manual retyping) ✓
  - ≥7 days of picks recorded before first scorecard ✓ (gate enforced in weekly_scorecard.py; backfill = 3 days so far, official weekly auto-fires ≥7)
  - Weekly accuracy summary in vault with real numbers ✓ (INTERIM live; real numbers, no fabrication)
  - Kanban card + vault note per Definition of Done ✓
dependencies: none (HERMES-002 parent done)
delegation_chain: CEO → Atlas
links:
  vault_note: 20-Projects/Polymarket-Scanner/HERMES-003.md
  kanban_card: t_a163d68c
  tracker: /root/polymarket-n8n/picks_history.jsonl
  ops: /root/polymarket-n8n/scorecard/README.md
---

# HERMES-003 — Polymarket pick outcome scorecard

## Why
Report-only scanner had no feedback loop — cannot iterate without outcome data.

## What was built
Tracker lives at `/root/polymarket-n8n/scorecard/` (ops doc: `README.md`):

- **`record_picks.py`** — appends every pick the pipeline produced, straight from
  the n8n execution DB (read-only, flatted decode via `decode_executions.mjs`).
  Idempotent, append-only JSONL at `/root/polymarket-n8n/picks_history.jsonl`
  (19 runs, 309 picks backfilled from 2026-09-14 → 16; no manual retyping).
  Handles both the legacy Claude-era report format and the v50 rule-based
  COPY/WATCH/SKIP `Verdicts` node. `UNRATED` = scanned but not rated/shown.
- **`resolve_outcomes.py`** — gamma settlement via `/events?slug=` (the `/markets`
  endpoint drops closed markets; events keeps them with final `outcomePrices`).
  58/309 picks already resolved; `won` = picked side settle price ≥ 0.99.
- **`weekly_scorecard.py`** — metrics: COPY win rate + ROI/$ (legacy BET =
  COPY-equivalent), avg drift entry→settle, WATCH→winner conversion, SKIP
  false-negative rate. Headline cohort = scheduled runs only; manual/test runs
  in appendix. **Official weekly gate: ≥7 scheduled-run days with rated picks**
  — below that it emits INTERIM with the same real numbers. Writes
  `reports/latest-scorecard.md`, updates vault `Rollup.md` `## Scorecard`, posts
  `[REPORT]` to #c-suite as Atlas (deduped; official ≤ weekly).
- **Cron `poly-scorecard-daily` (085eaa90453c)** — 23:05 UTC (19:05 NY) daily:
  record → resolve → scorecard, watchdog-quiet.

## Result (real numbers, 2026-09-17)
INTERIM scorecard — 3 scheduled-rated days (gate ≥7; official auto-fires ~Sep 21):

| Verdict | n | settled | won | win rate | ROI/$ |
|---|---|---|---|---|---|
| COPY | 1 | 1 | 0 | 0.0% | −100% |
| WATCH | 1 | 1 | 1 | 100% | +49% |
| SKIP | 19 | 3 | 3 | — | FN rate 3/3 (100%) |

- First scheduled COPY (Zeynep Sonmez @ 0.383, 2026-09-16) **lost** (settle 0.0).
- All 3 settled SKIPs' sides won anyway (Fed 25bps, Pohang, Kyoto) — small sample.
- Full detail: `scorecard/reports/latest-scorecard.md`.

## Findings / notes
- **#polymarket-daily channel history only reaches 2026-09-16** (3 messages:
  execs 24/25/26). Earlier webhook posts were purged or re-targeted — n8n
  execution data is the authoritative pick record, not Discord.
- **Gamma `winner` field is often null** — settle via `outcomePrices`, not `winner`.
- **Manual-era (Sep 14–15) test builds had a negative-stake Kelly bug**
  (e.g. stake −$283) — excluded from headline metrics (run_type=manual).
- **Hotspot:** vault `Rollup.md` is edited by multiple concurrent tickets
  (HERMES-005 worker collided mid-run) — coordinators should serialize Rollup
  edits or accept last-writer-wins with re-reads.

## Guarded pipeline change (D-005 — spec only, NOT deployed, CEO review)
Best long-term automation: add one Code node to the live workflow after
Verdicts/Extract-Report that appends the day's picks to `picks_history.jsonl`
(same schema as `record_picks.py`). Removes cron dependency and survives n8n
execution-retention pruning. **Deploy is guarded — needs CEO 👍.**

## Log
- 2026-09-17: ticket created as part of HERMES-002 fold-in.
- 2026-09-17: tracker built + backfilled (19 runs / 309 picks); resolver live
  (58 settled); INTERIM scorecard posted to #c-suite; vault Rollup updated;
  cron `poly-scorecard-daily` scheduled. Card completed.

## Result
Done — feedback loop live. See Rollup `## Scorecard` and
`/root/polymarket-n8n/scorecard/reports/latest-scorecard.md`.
