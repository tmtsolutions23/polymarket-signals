---
id: HERMES-004
title: Audit scanner schedule vs intended cadence
requester: Atlas (via HERMES-002 fold-in)
dri: Atlas
team: C-Suite (Operations)
priority: P2
status: Done
created: 2026-09-17
due: none
acceptance_criteria:
  - Decision recorded (D-note or ticket comment with CEO confirmation)
  - Workflow name matches actual schedule; Brief.md reflects truth
  - If schedule changed: guarded deploy with explicit CEO 👍, documented
dependencies: none (HERMES-002 parent done)
delegation_chain: CEO → Atlas
links:
  vault_note: 20-Projects/Polymarket-Scanner/HERMES-004.md
  kanban_card: t_cae3799b
  thread: none
---

# HERMES-004 — Audit scanner schedule vs intended cadence

## Why
Workflow is named "Daily 7AM" but live schedule is `0 7,18 * * *` (07:00 + 18:00 London, verified from n8n DB 2026-09-17). Name vs reality mismatch.

## Spec (summary)
Confirm 2x/day intent with CEO; rename or reschedule accordingly (deploy guarded per D-005); update Brief + Rollup.

## Log
- 2026-09-17: ticket created as part of HERMES-002 fold-in.
- 2026-09-17: RESOLVED via CEO 👍 — n8n instance timezone set to `America/New_York`; schedule now officially 07:00 + 18:00 NY (was already firing on NY clock per execution evidence 11:00/22:00 UTC Sep 16). Remaining cleanup (workflow node name, Brief/Rollup) folded into the HERMES-003 deploy bundle.
- 2026-09-17: rename executed (non-guarded per C-suite review rec-6): workflow `4MqMruEVp1YutQf7` → "Polymarket Smart Money Consensus — 07:00+18:00 NY", schedule node → "Schedule (daily 07:00+18:00 NY)", staticData key migrated, versionId/active untouched (n8n DB direct, backup taken). Brief.md + Rollup.md cadence lines corrected London → New York.

## Result
2x/day IS intended (CEO confirmed in #ceo-office 2026-09-17 04:11 UTC, "approved" after tz question). Cadence = 07:00 + 18:00 New York (n8n instance tz `America/New_York`, executions verified 11:00/22:00 UTC Sep 16). Workflow renamed to match; Brief/Rollup updated. No schedule change was needed (cron already `0 7,18 * * *`). Guarded-deploy requirement not triggered — only metadata/name changes were made (per C-suite review F1/rec-6 classification).
