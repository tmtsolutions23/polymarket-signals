# Polymarket Scanner — Project Brief

DRI: Atlas (COO) | Team: Operations (C-Suite) | Started: 2026-09-17

## Goal

Fold the daily Polymarket opportunity scanner (previously a standalone n8n pipeline posting to its own channel) into Hermes & Co. as a first-class company project, so we can iterate and improve it under org ownership. This reverses D-001 ("prod pipelines stay outside the org") **for this pipeline only** — per CEO request 2026-09-16 in #ceo-office.

## What the pipeline is (as-built, verified 2026-09-17)

**Workflow `4MqMruEVp1YutQf7` — "Polymarket Smart Money Consensus — 07:00+18:00 NY"** (n8n 1.123.79 on this VPS, active, v50, executionOrder v2):

- **Triggers:** schedule `0 * * * *` (hourly, instance tz `America/New_York`) + manual webhook `POST /webhook/poly-consensus` guarded by `x-consensus-key` secret header. **Change-detection gate (HERMES-010):** scans hourly but posts only on new/changed signals vs `last_posted.json` (same market+side with drift moved >2% and ≥90 min gap = "new" read); no-signal runs are silent (watcher + Midas digest cover health).
- **Signal:** leaderboard top-40 (by 1M PNL, >$0) → last 200 trades per trader → fresh BUYs only (≤48h) → group by outcome token → **consensus = ≥3 distinct top traders on the same side**
- **Verification (gamma-api):** match by event slug (fallback: clob token id), require market open, liquidity ≥ $5k, settles ≤ 7 days
- **Analysis:** Claude `claude-sonnet-4-5` (Anthropic) scores each pick; **verdicts are rule-based** (COPY/WATCH/SKIP): ≥3 traders, drift −30%..+6% from entry, ≤24h old, ≥$10k smart-money volume, price 0.01–0.99
- **Sizing:** half-Kelly with conviction premium (4–8%), per-pick cap 15% of bankroll, total exposure cap 25%
- **Output:** Discord post to **#polymarket-daily** via webhook `n8n-smart-money-consensus` (channel 1549644559859056740)
- **Bankroll:** `/root/polymarket-bankroll.txt` (default $100), updated via workflow `bankroll-update-001` (`POST /webhook/bankroll` `{"bankroll":N}`, guarded)
- **Creds:** Anthropic key `~/.n8n` credential (httpHeaderAuth), `.guard_secret` for manual trigger

**Product intent:** report-only smart-money copy signals (no auto-trading). The consensus IS the signal; LLM must not veto it (CEO directive 2026-09-15). User trades manually on Polymarket.

## Scope

**In:**
- Org ownership mapping, cadence integration, iteration loop (tickets) for this pipeline
- Vault docs, runbook, decision records
- Change control: any pipeline change flows through a kanban ticket; deploy to the live n8n workflow is a guarded action (CEO 👍)

**Out:**
- No pipeline behavior changes in this ticket (those come via iteration tickets HERMES-003+)
- No changes to other prod channels/crons (still covered by D-001)
- No auto-trading, no re-architecting, no host migration

## Success criteria

1. Project brief lives in `20-Projects/Polymarket-Scanner/` ✓
2. Pipeline ownership + cadence mapped to the org (D-005, Org-Chart, this brief) ✓
3. Iteration loop live: kanban tickets exist with DRIs, priorities, and acceptance criteria ✓
4. Change control documented: pipeline changes = ticket → review → guarded deploy ✓

## Key tickets

- HERMES-002 — this fold-in (done)
- HERMES-003 — pick outcome scorecard (P1) — close the feedback loop
- HERMES-004 — schedule/cadence mismatch audit (P2) — done 2026-09-17 (2x/day NY confirmed; renamed)
- HERMES-005 — failure alerting (P2)
- HERMES-006 — secrets hygiene (P3)

## Ownership & cadence (org mapping)

| Asset | Owner | Notes |
|---|---|---|
| Workflow `4MqMruEVp1YutQf7` + `bankroll-update-001` | Atlas (COO) — DRI | operations & execution |
| n8n host / systemd `n8n.service` | Atlas (COO) | infra under Ops |
| #polymarket-daily output channel | Atlas (COO) | project channel; content produced by pipeline |
| Bankroll value | CEO (human) | manual trading decisions; Atlas only stores it |
| Deploy/change to live pipeline | CEO approval | guarded action (D-001 reversal applies to ownership, not to deploy safety) |
| Signal methodology (consensus rules, Kelly) | CEO + Atlas | user's domain call; Atlas implements |

**Cadence:**
- Pipeline runs: hourly NY (cron `0 * * * *`), posts only on new/changed signals (change gate, HERMES-010)
- Failure alerting: watcher cron every 5 min → #polymarket-daily (fallback #blockers); missed-slot detection (HERMES-005, live 2026-09-17)
- Standup digest: scanner health (ran? errored? picks?) folded into Atlas standup
- Weekly [REPORT]: scanner status → picks shipped, error rate, open tickets
- Iteration loop: kanban board (Backlog → Ready → In-Progress → In-Review → Done); every change = ticket; ticket notes in this folder

## Risks

- **No outcome tracking** — today there is no scorecard: we cannot measure whether COPY signals win. Mitigation: HERMES-003.
- **Silent failure — MITIGATED (2026-09-17, HERMES-005):** if the workflow errors or a scheduled slot produces no run, the host-side watcher (`~/.hermes/scripts/n8n_failure_watcher.py`, cron `353e5ceabcbd` every 5 min) posts to #polymarket-daily within ~5 min (fallback #blockers), and the Atlas standup digest carries a run-health line. Watcher reads the local n8n DB; no n8n deploy needed (D-005-safe).
- **Secrets in workflow JSON** — guard key and Discord webhook URL embedded in workflow definition. Mitigation: HERMES-006.
- **Cadence drift** — resolved 2026-09-17 (HERMES-004): workflow renamed from "Daily 7AM" to "07:00+18:00 NY" to match the actual schedule; Brief/Rollup corrected from London to New York.
- **LLM veto risk** — Claude analysis could over-rule a live consensus; verdict logic is rule-based by design. Keep LLM advisory only.

## Links

- Vault: `20-Projects/Polymarket-Scanner/` (Brief, Log, Rollup, HERMES-XXX)
- Board: `hermes kanban` (D-004) — tickets HERMES-002..006
- Decisions: D-005 (this fold-in), D-001 (superseded for this pipeline)
