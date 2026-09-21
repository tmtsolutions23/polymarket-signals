# Polymarket Scanner — Staffing Plan (hiring)

**Status: CONTRACT ACTIVE (2026-09-17 → 2026-09-25) — Midas on watch (HERMES-009).**

## Why we are NOT hiring yet

1. **No proven capability gap.** No ticket has stalled or bounced (charter §10.2 gate). Atlas +
   the automated suite (pipeline, watcher, scorecard) cover current delivery end-to-end.
2. **The binding constraint is signal quality, not labor.** Interim scorecard: 0/1 COPY won,
   3/3 settled SKIPs won. More agents do not fix a weak signal — better gates + more data do.
3. **The decision point is data-driven:** the first official weekly scorecard (≥7 rated days,
   ~Sep 24) will show whether the consensus strategy wins at all. Hire after the verdict,
   not before.

## Contract hire trigger (any of)

- Official weekly scorecard shows COPY win rate < 50% for 2 consecutive weeks → need a
  dedicated analyst to rework gates/wallet selection.
- CEO wants daily human-curated market focus (which sports/events the scanner should
  emphasize) beyond the automated report.
- Rework/iteration backlog on this project exceeds 3 open tickets for 2 cycles.

## Spec if triggered: "Midas" — Polymarket Research Analyst (contract, 30 days)

- **Reports to:** Atlas (COO). **Team:** C-Suite (Operations) / future Research.
- **Mission:** turn scorecard data into profitable gate tuning + curate daily market focus.
- **KPIs:** weekly scorecard accuracy improvements; ≥1 evidence-based gate change per week
  while win rate < target; zero missed report days.
- **Kill criteria:** no measurable accuracy improvement after 2 scorecard cycles, OR COPY
  win rate still < 50% at contract end → retire (no permanent footprint).
- **Cost:** none (same Hermes instance, persona + webhook only — no new compute/spend).
- **Instantiation:** Daedalus (dormant, D-003) would run the hire flow — first real act
  for the Hiring Manager; requires CEO 👍 per guarded-action rule (contract agent: announce
  in #agent-registry with expiry).

## Guardrails

- Any gate/methodology change to the live workflow remains a guarded deploy (CEO 👍) —
  Midas proposes, CEO approves.
- Permanent hire only after the contract proves ≥3 consecutive weeks of improvement.

*Owner: Atlas | Reversible: yes | Date: 2026-09-17*
