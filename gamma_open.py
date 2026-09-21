import json, urllib.request, time

def get(url, t=30):
    req = urllib.request.Request(url, headers={"User-Agent": "poly-review"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=t) as r:
        return r.status, json.loads(r.read()), time.time() - t0

_, lb, _ = get("https://data-api.polymarket.com/v1/leaderboard?category=OVERALL&timePeriod=MONTH&orderBy=PNL&limit=3")
for w in [x["proxyWallet"] for x in lb]:
    _, tr, _ = get(f"https://data-api.polymarket.com/trades?user={w}&limit=100")
    for t in tr:
        if t.get("side") != "BUY" or not t.get("conditionId"):
            continue
        cid = t["conditionId"]
        try:
            s, m, dt = get(f"https://gamma-api.polymarket.com/markets?condition_ids={cid}")
        except Exception as e:
            print(f"ERR {e}"); continue
        if m:
            print(f"FOUND: trader buy {t.get('title')} | gamma: {m[0]['question']} | closed={m[0].get('closed')} | prices={m[0].get('outcomePrices')} | dt={dt:.1f}s")
            print("  trades outcome:", repr(t.get("outcome")), "| gamma outcomes:", m[0].get("outcomes"))
            print("  gamma condId match:", m[0].get("conditionId") == cid)
            raise SystemExit(0)
        else:
            print(f"empty: {t.get('title')[:60]} | cond={cid[:14]}... | eventSlug={t.get('eventSlug')}")
print("no open-market match found in sample")
