---
id: HERMES-008
title: Fix stale settle-date verification (gamma gate passes settled markets)
requester: Atlas (via HERMES-007 review finding F3)
dri: Atlas
team: C-Suite (Operations)
priority: P1
status: Done
created: 2026-09-17
due: none
acceptance_criteria:
  - Verification gate rejects already-settled/ended markets (no contradictory report lines)
  - Deployed via guarded flow with CEO 👍; webhook-tested
  - Brief/Rollup updated
dependencies: none
delegation_chain: CEO → Atlas
links:
  vault_note: 20-Projects/Polymarket-Scanner/HERMES-008.md
  kanban_card: t_dad31986
  thread: none
---

# HERMES-008 — Fix stale settle-date verification

## Why
Review finding F3: the gamma gate only rejected `settleDays > 7`, so markets with a
**negative** settleDays (already settled/ended) passed verification — producing
contradictory report lines ("settles today" header vs "already settled 3 days ago" reason)
and risking a COPY on a dead market.

## Fix (deployed)
`Verify & Enrich` now rejects a market when ANY of:
- `settleDays <= 0` (end date passed)
- `m.closed === true`
- `m.active === false`
- `liquidity < 5000`

## Log
- 2026-09-17: ticket created from HERMES-007 review finding.
- 2026-09-17: bundled with F4 noise pre-filter + NY rename (bundle v2, CEO-approved); deployed via DB + `workflow_history` (version 30771862, counter 57); workflow activated, webhook test runs 28/29 success, live report confirmed new pre-filter path.

## Result
Done — settled markets are excluded at the gate; no stale picks can reach the report.
