import sqlite3, json

db = sqlite3.connect('/root/.n8n/.n8n/database.sqlite')
row = db.execute("SELECT nodes, connections FROM workflow_entity WHERE id='4MqMruEVp1YutQf7'").fetchone()
nodes = json.loads(row[0])
conns = json.loads(row[1])

print("=== CONNECTIONS (full) ===")
for src, v in conns.items():
    for out_type, outs in v.items():
        for out in outs:
            for t in out:
                print("  %s --%s--> %s (index %s)" % (src, out_type, t.get('node'), t.get('index')))

print("\n=== VERIFY & ENRICH / gate code ===")
for n in nodes:
    if n.get('name') in ('Verify & Enrich', 'Verify Query', 'HTTP Gamma (verify markets)'):
        p = n.get('parameters', {})
        code = p.get('jsCode') or p.get('code') or p.get('url') or ''
        print("\n--- %s ---" % n.get('name'))
        print(code[:4000])

print("\n=== EXECUTION HISTORY (last 12) ===")
for r in db.execute("SELECT id, startedAt, stoppedAt, mode, status FROM execution_entity WHERE workflowId='4MqMruEVp1YutQf7' ORDER BY id DESC LIMIT 12"):
    print("  #%s %s %s %s dur=%s" % (r[0], r[1], r[4], r[3], r[2]))
