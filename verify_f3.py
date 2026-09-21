import json, urllib.request, datetime

req = urllib.request.Request(
    "https://gamma-api.polymarket.com/events?slug=sao-paulo-open-vendula-valdmannova-vs-laura-pigossi",
    headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
             "Accept": "application/json"})
with urllib.request.urlopen(req, timeout=25) as r:
    data = json.loads(r.read().decode())

evs = data if isinstance(data, list) else [data]
for ev in evs[:1]:
    print('event:', ev.get('slug'), '| closed:', ev.get('closed'), '| markets:', len(ev.get('markets', [])))
    for m in ev.get('markets', []):
        end = m.get('endDate')
        if not end:
            continue
        end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
        days = (end_dt - datetime.datetime.now(datetime.timezone.utc)).total_seconds() / 86400
        closed = m.get('closed')
        active = m.get('active')
        new_gate = "REJECT" if (days <= 0 or days > 7 or closed is True or active is False) else "ACCEPT"
        print(f"  market: {m.get('slug')} | closed={closed} active={active} endDate={end}")
        print(f"    settleDays={days:+.1f} | NEW gate: {new_gate}")
