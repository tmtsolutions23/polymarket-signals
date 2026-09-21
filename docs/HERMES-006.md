---
id: HERMES-006
title: Secrets hygiene on scanner workflows
requester: Atlas (via HERMES-002 fold-in)
dri: Atlas
team: C-Suite (Operations)
priority: P3
status: Backlog
created: 2026-09-17
due: none
acceptance_criteria:
  - No live webhook URL or guard secret in workflow node parameters (verified via n8n DB)
  - Manual trigger guard still intact
  - Exported/checked-in workflow files redacted
  - Deploy guarded (D-005): CEO 👍 before touching live workflow
dependencies: none (HERMES-002 parent done)
delegation_chain: CEO → Atlas
links:
  vault_note: 20-Projects/Polymarket-Scanner/HERMES-006.md
  kanban_card: t_3ba50013
  thread: none
---

# HERMES-006 — Secrets hygiene on scanner workflows

## Why
Live workflow JSON embeds the #polymarket-daily webhook URL and x-consensus-key guard in plaintext; /root/polymarket-n8n exports contain them too.

## Spec (summary)
Move webhook URL + guard key into n8n credentials/env; redact exports; keep guard functional.

## Log
- 2026-09-17: ticket created as part of HERMES-002 fold-in.

## Result
_(pending)_
