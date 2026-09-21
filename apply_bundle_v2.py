#!/usr/bin/env python3
"""Revert in-workflow Pick Log node; keep F3 fix + pre-filter + rename (v2 bundle)."""
import json

SRC = '/root/polymarket-n8n/live_workflow.json'
DST = '/root/polymarket-n8n/edited_workflow_v2.json'

d = json.load(open(SRC))
d['name'] = 'Polymarket Smart Money Consensus — 07:00+18:00 NY'
d.pop('versionId', None)

# --- F3 fix (Verify & Enrich) ---
for n in d['nodes']:
    if n['name'] == 'Verify & Enrich':
        c = n['parameters']['jsCode']
        assert c.count("if (m.closed === true || liq < 5000) continue;") == 1
        c = c.replace("if (m.closed === true || liq < 5000) continue;",
                      "if (m.closed === true || m.active === false || liq < 5000) continue;")
        old = "  if (settleDays !== null && settleDays > 7) continue; // no long holds — fast copy trading only"
        assert c.count(old) == 1, 'settle line not found'
        c = c.replace(old,
                      "  // F3 fix: settleDays <= 0 = market already settled/ended — reject, was passing before\n"
                      "  if (settleDays !== null && (settleDays <= 0 || settleDays > 7)) continue; // no settled markets, no long holds")
        n['parameters']['jsCode'] = c

# --- Noise pre-filter + slug/asset passthrough (Prompt & Route) ---
for n in d['nodes']:
    if n['name'] == 'Prompt & Route':
        c = n['parameters']['jsCode']
        assert c.count("const picks = inputItems.slice(0, 10);") == 1
        c = c.replace("const picks = inputItems.slice(0, 10);",
                      "// Noise pre-filter (HERMES-007 F4): only >= $10k smart-money volume reaches the report\n"
                      "const picks = inputItems.filter(p => (p.totalUsd || 0) >= 10000).slice(0, 10);\n"
                      "if (!picks.length) {\n"
                      "  return [{ json: { skip: true, message: 'No signals above $10k smart-money this run.' } }];\n"
                      "}")
        assert c.count("    url: p.marketUrl\n  };") == 1
        c = c.replace("    url: p.marketUrl\n  };",
                      "    url: p.marketUrl,\n"
                      "    slug: p.slug,\n"
                      "    asset: String(p.asset)\n"
                      "  };")
        n['parameters']['jsCode'] = c

# --- Extract Report: fully original (no picksLog, no structured entries) ---
# live_workflow.json IS the original, so nothing to do here.

# --- connections: fix stale schedule key (same fix as before) ---
conns = d['connections']
if 'Schedule (daily 07:00 London)' in conns:
    conns['Schedule (daily 07:00+18:00 NY)'] = conns.pop('Schedule (daily 07:00 London)')

# sanity
names = {n['name'] for n in d['nodes']}
for src, cv in conns.items():
    assert src in names, f"src {src} missing"
    for arr in cv['main']:
        for c in arr:
            assert c['node'] in names, f"target {c['node']} missing"

json.dump(d, open(DST, 'w'), indent=1)
print('wrote', DST, '| nodes:', len(d['nodes']), '| name:', d['name'])
print('no Pick Log node:', all(n['name'] != 'Pick Log (scorecard)' for n in d['nodes']))
