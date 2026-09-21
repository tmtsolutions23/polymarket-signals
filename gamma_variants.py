import json, urllib.request, time

def get(url, t=30):
    req = urllib.request.Request(url, headers={"User-Agent": "poly-review"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=t) as r:
        return r.status, json.loads(r.read()), time.time() - t0

_, lb, _ = get("https://data-api.polymarket.com/v1/leaderboard?category=OVERALL&timePeriod=MONTH&orderBy=PNL&limit=5")
wallet = lb[0]["proxyWallet"]
_, tr, _ = get(f"https://data-api.polymarket.com/trades?user={wallet}&limit=200")
buys = [t for t in tr if t.get("side") == "BUY" and t.get("conditionId") and (t.get("timestamp", 0) * 1000) > (time.time() - 48*3600) * 1000]
t0 = buys[0]
print("trades item keys:", sorted(t0.keys()))
print("conditionId:", t0["conditionId"])
print("asset:", t0.get("asset"))
print("slug:", t0.get("slug"), "| eventSlug:", t0.get("eventSlug"), "| outcome:", t0.get("outcome"))

tests = [
    ("condition_ids (hex cond)", f"https://gamma-api.polymarket.com/markets?condition_ids={t0['conditionId']}"),
    ("conditionIds camel", f"https://gamma-api.polymarket.com/markets?conditionIds={t0['conditionId']}"),
    ("condition_id singular", f"https://gamma-api.polymarket.com/markets?condition_id={t0['conditionId']}"),
    ("clob_token_ids", f"https://gamma-api.polymarket.com/markets?clob_token_ids={t0['asset']}"),
    ("slug", f"https://gamma-api.polymarket.com/markets?slug={t0.get('slug')}"),
]
for name, url in tests:
    try:
        s, body, dt = get(url)
        try:
            n = len(json.loads(body))
        except Exception:
            n = f"non-json: {body[:80]!r}"
        print(f"{name}: status={s} items={n} in {dt:.1f}s")
    except Exception as e:
        print(f"{name}: ERROR {e}")
