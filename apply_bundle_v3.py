#!/usr/bin/env python3
"""HERMES-010: hourly scan + change-detection gate (v3).

Changes on top of the live base:
- Schedule: `0 7,18 * * *` -> `0 * * * *` (hourly), node renamed.
- New node 'Change Gate (new signals)' between US Availability Gate and Prompt & Route:
  $10k filter + dedupe vs /root/polymarket-n8n/last_posted.json (fail-open).
- New node 'Silent (no signal)' -> both IF skip branches; 'Discord: no picks' removed.
- Workflow renamed to '... Hourly NY'.
"""
import json

SRC = '/root/polymarket-n8n/live_base_v3.json'
DST = '/root/polymarket-n8n/edited_workflow_v3.json'

d = json.load(open(SRC))
d['name'] = 'Polymarket Smart Money Consensus — Hourly NY'
d.pop('versionId', None)

def get(name):
    for n in d['nodes']:
        if n['name'] == name:
            return n
    raise SystemExit(f'node not found: {name}')

# --- 1. schedule -> hourly ---
sched = get('Schedule (daily 07:00+18:00 NY)')
assert sched['parameters']['rule']['interval'][0]['field'] == 'cronExpression'
sched['parameters']['rule']['interval'][0]['expression'] = '0 * * * *'
sched['name'] = 'Schedule (hourly NY)'

# --- 2. Change Gate node ---
GATE_CODE = """// Change gate (HERMES-010): drop sub-$10k noise and post only NEW/changed signals
// vs the last posted report. Fail-open: state-file issues degrade to "post everything"
// (current behavior) — never break the signal pipeline.
let fs = null;
try { fs = require('fs'); } catch (e) { fs = null; }
const STATE = '/root/polymarket-n8n/last_posted.json';
const MIN_USD = 10000;
const RE_POST_MIN_GAP_MS = 90 * 60 * 1000;   // min gap before re-posting a drifted signal
const DRIFT_TOLERANCE = 2;                    // % drift change that makes a signal "new" again

const all = $input.all().map(i => i.json);
if (!all.length || (all.length === 1 && all[0] && all[0].skip === true)) {
  return [{ json: { skip: true, silent: true } }];
}
const picks = all.filter(p => p && p.asset && (p.totalUsd || 0) >= MIN_USD);
if (!picks.length) {
  return [{ json: { skip: true, silent: true, message: 'No signals above $10k smart-money this run.' } }];
}

const dateKey = new Date().toISOString().slice(0, 10);
let state = { date: dateKey, signals: {} };
if (fs) {
  try {
    const parsed = JSON.parse(fs.readFileSync(STATE, 'utf8'));
    if (parsed && parsed.date === dateKey && parsed.signals) state = parsed;
  } catch (e) {}
}
const signals = state.signals || {};
const fresh = [];
const now = Date.now();
for (const p of picks) {
  const key = String(p.slug || p.title || '') + '|' + String(p.outcome || '');
  const drift = (p.avgEntryPrice > 0 && p.currentPrice != null)
    ? +(((p.currentPrice - p.avgEntryPrice) / p.avgEntryPrice) * 100).toFixed(1)
    : null;
  const prev = signals[key];
  const drifted = prev && prev.drift != null && drift != null && Math.abs(drift - prev.drift) > DRIFT_TOLERANCE;
  const gapOk = !prev || !prev.ts || (now - new Date(prev.ts).getTime()) >= RE_POST_MIN_GAP_MS;
  const isNew = !prev || (drifted && gapOk);
  // Fix: only anchor drift/ts to the LAST POSTED state, not every scan. The pipeline
  // scans hourly (60min) but requires a 90min gap before a drift-based repost — if this
  // update ran unconditionally, prev.ts/prev.drift tracked the last *scan* instead of the
  // last *post*, so gapOk could never be true and drift was compared hour-over-hour
  // instead of since-last-post, silently muting reposts for any signal that kept
  // reappearing every scan (exactly the slow-drift case this gate exists to catch).
  if (isNew) {
    signals[key] = { drift, ts: new Date().toISOString() };
    fresh.push(p);
  }
}
if (fs) {
  try { fs.writeFileSync(STATE, JSON.stringify(state)); } catch (e) { console.error('[change gate] state write failed: ' + e.message); }
}
if (!fresh.length) {
  return [{ json: { skip: true, silent: true, message: 'No new signals since last report.' } }];
}
return fresh.map(p => ({ json: p }));"""

d['nodes'].append({
    "id": "00000000-0000-4000-8000-0000000000c1",
    "name": "Change Gate (new signals)",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1920, 400],
    "parameters": {"mode": "runOnceForAllItems", "jsCode": GATE_CODE},
})

# --- 3. Silent node ---
d['nodes'].append({
    "id": "00000000-0000-4000-8000-0000000000c2",
    "name": "Silent (no signal)",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [2160, 60],
    "parameters": {"mode": "runOnceForAllItems", "jsCode": "return [];"},
})

# --- 4. Rewire ---
conns = d['connections']
# fix schedule key
if 'Schedule (daily 07:00+18:00 NY)' in conns:
    conns['Schedule (hourly NY)'] = conns.pop('Schedule (daily 07:00+18:00 NY)')
# US Availability Gate -> Change Gate (insert between it and Prompt & Route)
ug = conns['US Availability Gate']['main'][0]
assert ug[0]['node'] == 'Prompt & Route', ug
ug[0] = {"node": "Change Gate (new signals)", "type": "main", "index": 0}
conns['Change Gate (new signals)'] = {"main": [[{"node": "Prompt & Route", "type": "main", "index": 0}]]}
# IF skip branches -> Silent
for ifname in ('IF has picks', 'IF has verified picks'):
    main = conns[ifname]['main']
    assert main[0][0]['node'] == 'Discord: no picks', (ifname, main[0])
    main[0] = [{"node": "Silent (no signal)", "type": "main", "index": 0}]
conns['Silent (no signal)'] = {"main": [[]]}
# remove Discord: no picks node + connections
conns.pop('Discord: no picks', None)
d['nodes'] = [n for n in d['nodes'] if n['name'] != 'Discord: no picks']

# sanity
names = {n['name'] for n in d['nodes']}
for src, cv in conns.items():
    assert src in names, f'src {src} missing'
    for arr in cv['main']:
        for c in arr:
            assert c['node'] in names, f'target {c["node"]} missing'

json.dump(d, open(DST, 'w'), indent=1)
print('wrote', DST, '| nodes:', len(d['nodes']))
print('schedule:', get('Schedule (hourly NY)')['parameters']['rule']['interval'][0]['expression'])
