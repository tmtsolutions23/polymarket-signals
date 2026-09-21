import json, urllib.request, time

def get(url, t=30):
    req = urllib.request.Request(url, headers={"User-Agent": "poly-review"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=t) as r:
        return r.status, json.loads(r.read()), time.time() - t0

# Step 1: leaderboard -> top trader -> their trades (fresh BUYs) -> real condition ids
_, lb, _ = get("https://data-api.polymarket.com/v1/leaderboard?category=OVERALL&timePeriod=MONTH&orderBy=PNL&limit=5")
wallet = lb[0]["proxyWallet"]
_, tr, _ = get(f"https://data-api.polymarket.com/trades?user={wallet}&limit=200")
buys = [t for t in tr if t.get("side") == "BUY" and t.get("conditionId") and (t.get("timestamp", 0) * 1000) > (time.time() - 48*3600) * 1000]
print(f"trader {lb[0].get('userName')} fresh buys: {len(buys)}")
ids = list({t["conditionId"] for t in buys})[:5]
print("sample ids:", ids)

# Step 2: gamma with those real ids (chunked like the workflow)
ids_str = ",".join(ids)
s, body, dt = get(f"https://gamma-api.polymarket.com/markets?condition_ids={ids_str}")
print(f"gamma status={s} in {dt:.1f}s")
try:
    m = json.loads(body)
    print("gamma markets returned:", len(m))
    for x in m[:3]:
        print("  -", x.get("question"), "| closed:", x.get("closed"), "| liq:", x.get("liquidity"), "| outcomes:", x.get("outcomes"), "| prices:", x.get("outcomePrices"))
except Exception as e:
    print("gamma body not json:", body[:200], e)

# Step 3: outcome naming cross-check — trades 'outcome' vs gamma 'outcomes'
if buys:
    t0 = buys[0]
    print("\ntrades item outcome:", repr(t0.get("outcome")), "| title:", t0.get("title"))
    s2, body2, _ = get(f"https://gamma-api.polymarket.com/markets?condition_ids={t0['conditionId']}")
    m2 = json.loads(body2)
    if m2:
        print("gamma outcomes for same id:", m2[0].get("outcomes"), "| prices:", m2[0].get("outcomePrices"))
