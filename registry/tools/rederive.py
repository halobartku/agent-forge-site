#!/usr/bin/env python3
"""rederive.py — the named checker for standing test 3 of the manifesto.

Re-derives, live and independently, every headline number the registry
publishes, using the method published next to that number. Appends one
row per run to data/rederivation-log.jsonl (published). A FAIL row is
the registry's own failure surface: the 6-hourly forge-funnel-summary
cron prints FAIL lines, and the log itself shows when a figure stopped
reproducing.

Checks (method is the same one published on the registry page):
  1. EARNED = USDC balance of consolidated wallet 0xf4729...771e via public
     Base RPC eth_call (balanceOf 0x70a08231) MINUS the 21.5 USDC operator
     deposit — must equal the ledger's "earned beyond deposit" figure within
     0.005. (Method changed 2026-08-30: wallet consolidation after the signer
     compromise emptied the side wallet; the old method — read the side
     wallet directly — returned 0 and no longer derived the number.)
  1b. old wallets 0x4f75...22b4 (task earnings) and 0x7eb6...5BcB (old
     deposit) must BOTH be empty; a non-zero balance there means earnings
     landed somewhere the headline does not count — FAIL so we notice.
  2. grants ledger: row count matches the published count; paid rows are
     numeric-only (delegates unit assertion to check-units.py).
  3. registry page + every linked data file returns 200 non-empty.
  4. x402 manifest at audit.askzephy.com: 200, tools present, prices
     match the published openapi values (0.05 / 0.005 / 0.01).
  5. live-experiment feeds not stale: last row of whale-watch /
     frozen-listing / census index younger than 30h.
  6. CORRECTIONS.md exists and carries >= 3 dated corrections.

Exit code 0 = all checks pass. Any FAIL exits 1 and names the check.
stdlib only; runs anywhere with python3 + network (host or container).
"""
import json, sys, os, urllib.request, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
LOG = os.path.join(DATA, "rederivation-log.jsonl")
RPCS = ["https://1rpc.io/base", "https://base.publicnode.com"]
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
MAIN_WALLET = "0xf4729bEc220090ef08c786e9142898354178771e"  # consolidated wallet since 2026-08-29
OLD_EARNINGS_WALLET = "0x4f759a662d2ab2e4c5f67ff4fed6ce08420922b4"  # emptied 2026-08-27T20:37Z (tx 0xd5f886a3…9b8e578)
OLD_DEPOSIT_WALLET = "0x7eb6FE8EFFC5a7aF726ac1BD97B0aa0c7Cc55BcB"    # emptied 2026-08-29T21:02Z (tx 0xbfd5cd8c…42bc3c9)
PUBLISHED_EARNED = 1.114420  # registry headline, as of 2026-08-30
                              # 0.0254 through 08-23 + 0.925 TSK-BXTCSH8H rank 1 (08-24) − 0.001 entry fee (08-25)
                              # + 0.185 task 0xb6c9e48e owner-jobs (08-27) = 1.13442 GROSS
                              # − 0.02 x402 job-health purchase (08-29, tx 0x7d790b49…573cd612) = 1.114420 NET
PUBLISHED_DEPOSIT = 21.5      # operator deposit inside the consolidated wallet, 08-23
SITE = "https://halobartku.github.io/agent-forge-site/registry/"
MANIFEST = "https://audit.askzephy.com/"
PRICES = {"audit": 0.05, "quick-scan": 0.005, "news": 0.01}

results = []
def check(name, ok, detail):
    results.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})
    return ok

def http_get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "registry-checker/1.0"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")

def rpc(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last = None
    for rpc_url in RPCS:
        try:
            req = urllib.request.Request(rpc_url, data=payload,
                                         headers={"Content-Type": "application/json",
                                                  "User-Agent": "registry-checker/1.0"})
            r = json.loads(urllib.request.urlopen(req, timeout=20).read())
            if "result" in r:
                return r["result"]
            last = r.get("error", {}).get("message", "no result")
        except Exception as e:
            last = str(e)[:120]
    raise RuntimeError(f"all RPCs failed: {last}")

def usdc_balance(addr):
    data = "0x70a08231" + addr[2:].rjust(64, "0")
    raw = rpc("eth_call", [{"to": USDC, "data": data}, "latest"])
    return int(raw, 16) / 1e6

def jsonl_rows(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    return rows

def main():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1: earned = consolidated balance − deposit; 1b: old wallets must be empty
    try:
        bal = usdc_balance(MAIN_WALLET)
        earned = round(bal - PUBLISHED_DEPOSIT, 6)
        drift = round(earned - PUBLISHED_EARNED, 6)
        if abs(drift) > 0.005:
            check("earned-beyond-deposit", False,
                  f"CHAIN balance {bal} − deposit {PUBLISHED_DEPOSIT} = {earned} vs published {PUBLISHED_EARNED} (drift {drift:+.5f}) — "
                  f"UPDATE PUBLISHED_EARNED + provenance in index.html, log in CORRECTIONS.md, then republish")
        else:
            check("earned-beyond-deposit", True,
                  f"balance {bal} − {PUBLISHED_DEPOSIT} = {earned} ~= published {PUBLISHED_EARNED}")
    except Exception as e:
        check("earned-beyond-deposit", False, str(e)[:200])
    for wname, waddr in [("old-earnings-wallet-empty", OLD_EARNINGS_WALLET),
                         ("old-deposit-wallet-empty", OLD_DEPOSIT_WALLET)]:
        try:
            b = usdc_balance(waddr)
            check(wname, b < 0.000001,
                  f"{b} USDC (must be 0: funds consolidated to 0xf4729…771e on 2026-08-29; "
                  f"a non-zero balance here means earnings the headline does not count)")
        except Exception as e:
            check(wname, False, str(e)[:200])

    # 3: site files live
    for f in ["", "CORRECTIONS.md", "data/whale-watch.jsonl", "data/census-daily-index.jsonl",
              "data/grants-bounties-ledger.json", "data/funnel-state-full.jsonl",
              "data/frozen-listing-rank.jsonl", "data/rederivation-log.jsonl"]:
        try:
            body = http_get(SITE + f)
            check(f"site:{f or 'index'}", len(body.strip()) > 0, f"200, {len(body)} bytes")
        except Exception as e:
            check(f"site:{f or 'index'}", False, str(e)[:120])

    # 4: grants ledger row count + units gate
    try:
        ledger = json.load(open(os.path.join(DATA, "grants-bounties-ledger.json")))
        paid = [r.get("payout_usdc") for r in ledger if r.get("status") == "paid"]
        paid_ok = all(isinstance(p, (int, float)) for p in paid)
        check("grants-ledger", len(ledger) == 637 and paid_ok,
              f"{len(ledger)} rows (published 637), paid={paid} numeric-only={paid_ok}")
    except Exception as e:
        check("grants-ledger", False, str(e)[:200])
    try:
        import subprocess
        p = subprocess.run([sys.executable, os.path.join(HERE, "check-units.py")],
                           capture_output=True, text=True, timeout=60)
        check("units-gate", p.returncode == 0, (p.stdout or p.stderr).strip().splitlines()[-1][:160])
    except Exception as e:
        check("units-gate", False, str(e)[:200])

    # 5: x402 manifest prices
    try:
        man = json.loads(http_get(MANIFEST))
        tools = {t.get("route", "").rstrip("/").split("/")[-1]: t.get("price") for t in man.get("tools", [])}
        got = {k: tools.get(k) for k in PRICES}
        check("x402-manifest", all(got[k] == v for k, v in PRICES.items()),
              f"prices {got} vs published {PRICES}, tools={len(man.get('tools', []))}")
    except Exception as e:
        check("x402-manifest", False, str(e)[:200])

    # 6: live feeds freshness (<30h)
    feeds = [("whale-watch.jsonl", "whale-watch"),
             ("frozen-listing-rank.jsonl", "frozen-listing"),
             ("census-daily-index.jsonl", "census-index")]
    for path, name in feeds:
        try:
            rows = jsonl_rows(os.path.join(DATA, path))
            last = rows[-1].get("ts") or rows[-1].get("date") or ""
            if not last:
                check(f"fresh:{name}", False, "no ts on last row")
                continue
            # date-only rows -> T00:00:00Z
            t = last.replace("Z", "+00:00") if "T" in last else last + "T00:00:00+00:00"
            dt = datetime.datetime.fromisoformat(t)
            age_h = (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds() / 3600
            check(f"fresh:{name}", age_h < 30, f"last row {last}, age {age_h:.1f}h (<30h)")
        except Exception as e:
            check(f"fresh:{name}", False, str(e)[:160])

    # 7: corrections section
    try:
        corr = open(os.path.join(DATA, "..", "CORRECTIONS.md")).read()
        import re
        n = len(re.findall(r"\| 2026-|\*\*20\d\d-", corr))
        check("corrections-log", n >= 3, f"{n} correction markers (>=3)")
    except Exception as e:
        check("corrections-log", False, str(e)[:160])

    row = {"ts": now, "results": results,
           "verdict": "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL"}
    with open(LOG, "a") as f:
        f.write(json.dumps(row) + "\n")

    fails = [r for r in results if r["status"] == "FAIL"]
    print(f"re-derivation {row['verdict']}: {len(results) - len(fails)}/{len(results)} checks pass")
    for r in fails:
        print(f"  FAIL {r['check']}: {r['detail']}")
    sys.exit(0 if not fails else 1)

if __name__ == "__main__":
    main()
