---
id: HERMES-002
title: Fold Polymarket scanner project into the company
requester: CEO
dri: Atlas
team: C-Suite (Operations)
priority: P1
status: Done
created: 2026-09-17
due: none
acceptance_criteria:
  - Project brief in 20-Projects/ (Polymarket-Scanner/Brief.md)
  - Pipeline ownership + cadence mapped to org (D-005, Org-Chart, Brief ownership table)
  - Iteration loop live: kanban tickets HERMES-003..006 with DRIs, priorities, acceptance criteria
dependencies: none
delegation_chain: CEO → Atlas
links:
  vault_note: 20-Projects/Polymarket-Scanner/HERMES-002.md
  kanban_card: t_b3ae5e4c
  thread: none
---

# HERMES-002 — Fold Polymarket scanner project into the company

## Log
- 2026-09-17: inspected live n8n workflows (4MqMruEVp1YutQf7 + bankroll-update-001) from the DB — verified triggers, nodes, consensus logic, gamma verification, Kelly sizing, Discord target (#polymarket-daily via webhook n8n-smart-money-consensus).
- 2026-09-17: created 20-Projects/Polymarket-Scanner/ (Brief, Log, Rollup).
- 2026-09-17: recorded D-005 (reverses D-001 for this pipeline), updated Org-Chart, Kanban index, Metrics.
- 2026-09-17: created iteration tickets HERMES-003..006 (scorecard P1, cadence audit P2, failure alerting P2, secrets hygiene P3).
- 2026-09-17: added Discord webhooks for ceo-office/kanban/decisions to scaffold + webhooks.json (7 persona channels), so DoD notifications can be posted.

## Result
Polymarket scanner is now a company project: brief + ownership + cadence + change control documented; iteration loop (tickets) live on the board. Pipeline itself untouched (deploys remain guarded per D-005).
