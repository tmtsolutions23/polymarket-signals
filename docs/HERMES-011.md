---
id: HERMES-011
title: Kalshi smart-money consensus scanner (visible-trader fresh-buy signals)
requester: CEO ("hold what they hold" — next phase)
dri: Atlas (Midas on contract)
team: C-Suite (Operations)
priority: P1
status: In-Progress
created: 2026-09-20
due: none
acceptance_criteria:
  - Pull all 3 leaderboards (volume/markets/pnl, monthly)
  - Identify traders with public trades (visibility=visible)
  - Fresh-buy consensus (>=2 whales same market+side, 48h) + single-whale moves (>= $2k)
  - Current holdings reconstruction per visible whale (7-day netting, maker+taker sides)
  - Hold consensus (>=2 whales holding same side) + big-holds view (>= $5k)
  - Cron 07:00/19:00 UTC → #midas; AUTH_FAIL instructs CEO to refresh cURL
dependencies: none (Kalshi session creds from CEO)
delegation_chain: CEO → Atlas
links:
  vault_note: 20-Projects/Polymarket-Scanner/HERMES-011.md
  kanban_card: t_37aa5d07
  thread: none
---

# HERMES-011 — Kalshi smart-money scanner

## Why
CEO: "we want to hold what they hold while disregarding clear arbitrage cases and hedging" on Kalshi — the top-volume, highest-PnL traders that opt into public trade sharing.

## Findings (2026-09-20)
- 158 unique traders across leaderboards; only **5 visible** (share trades publicly): jake6767, szg.szg, weatherman.allday, stevefink, the.hoff.85 (~3% opt-in rate).
- `/social/trades?nickname=X` exposes full identity-tagged trade history for visible traders (market, side, price, size, ts) — Polymarket-equivalent signal granularity.
- Consensus (≥2 whales same side 48h) rarely fires with 5 visible traders; **single-whale + hold views are the practical signal**.
- Live example: jake6767 holds 37,585 YES on NFL Bills -10 @ $0.279 (≈$10.5k); szg.szg actively trades BTC 15-min range markets ($17k-$30k positions).

## Delivered
- `kalshi_consensus.py`: leaderboards → visibility scan → trade history (7d) → fresh buys / holdings / hold-consensus → compact #midas report.
- Cron `f339f30bf87f` 07:00 & 19:00 UTC → #midas (no_agent).
- Effective-price fix: Kalshi reports YES price on NO trades → vwap/USD use (1−p) for NO side.

## Log
- 2026-09-20: v1 (fresh buys) live → v2 (holdings + big holds) deployed after CEO "go".
- 2026-09-20: **v3 classification (CEO "go")**: per-whale style labels — `arb` (same-ticker both-sides ≥25% of markets), `scalper` (<1h holds, ≥20 trades), `directional`. Signals filtered to directional only. Open-position hold spans count from entry→now (was falsely 0h). Live labels: jake6767=directional (129h), stevefink=directional (15h), the.hoff.85=directional (11h), weatherman.allday=directional (3h), szg.szg=arb (76% mixed, excluded). Big holds now show only directional conviction: jake6767 Bills -10 $10.5k, Steelers $9.8k, tennis USO $7.2k.
- 2026-09-20: verified cron-mode output end-to-end; AUTH_FAIL path tells CEO to paste fresh cURL.

## Result
Done. Kalshi is a **directional single-whale/hold** signal venue (opt-in sharing, arb-filtered). Polymarket remains the multi-whale-consensus play. Future: widen pool to top 500 for more visible whales; add settle-window + liquidity gates per hold signal.