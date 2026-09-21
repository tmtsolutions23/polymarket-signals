import json, urllib.request, time

def get(url, t=30):
    req = urllib.request.Request(url, headers={"User-Agent": "poly-review"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=t) as r:
        return r.status, json.loads(r.read()), time.time() - t0

# Open market: Cowboys vs Giants tonight
ev = "nfl-dal-nyg-2026-09-14"
# 1) events by slug
try:
    s, data, dt = get(f"https://gamma-api.polymarket.com/events?slug={ev}")
    if data:
        e = data[0]
        print(f"EVENT OK ({dt:.1f}s): {e.get('title')} | active={e.get('active')} closed={e.get('closed')} | markets={len(e.get('markets', []))}")
        for m in e.get("markets", [])[:6]:
            print("   market:", m.get("slug"), "| outcomes:", m.get("outcomes"), "| prices:", m.get("outcomePrices"), "| clob:", (m.get("clobTokenIds") or "")[:40], "...")
    else:
        print("EVENT EMPTY for", ev)
except Exception as e:
    print("EVENT ERR:", e)

# 2) markets by slug for the open market
mkt = "epl-cov-bri-2026-09-13-bri"  # yesterday's (control)
try:
    s, data, dt = get(f"https://gamma-api.polymarket.com/markets?slug={mkt}")
    print(f"MARKET slug '{mkt}': {len(data)} items ({dt:.1f}s)")
except Exception as e:
    print("MARKET ERR:", e)
