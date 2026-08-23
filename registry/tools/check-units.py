#!/usr/bin/env python3
"""Publish-time checks for registry data files.

Born from A.72 defect #1 (2026-08-23): payout_usdc carried 348 raw integer
base-unit strings ("6000000" = 6 USDC), so any naive sum of the column was
wrong by six decimal places — on a surface whose pitch is re-derivable numbers.

Rules enforced (exit 1 + loud message on violation):
  1. payout_usdc: null or a NUMBER in USDC units (never a string, never base units).
  2. offer_base_units: null or an INTEGER; offer_asset/offer_decimals required
     alongside any non-null offer_base_units.
  3. No string may appear in any field named *_usdc.
"""
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
LEDGER = DATA / "grants-bounties-ledger.json"

errors = []


def check(name, ok, msg):
    print(("PASS " if ok else "FAIL ") + name + (" — " + msg if msg else ""))
    if not ok:
        errors.append(name + ": " + msg)


def main():
    rows = json.loads(LEDGER.read_text())
    check("ledger-load", isinstance(rows, list) and len(rows) > 0, f"{len(rows)} rows")

    bad_payout = [r for r in rows if not (
        r.get("payout_usdc") is None or isinstance(r.get("payout_usdc"), (int, float))
        and not isinstance(r.get("payout_usdc"), bool)
    )]
    check("payout_usdc-units", not bad_payout,
          f"{len(bad_payout)} rows carry non-numeric payout_usdc (must be null or number in USDC)")

    bad_offer = [r for r in rows if not (
        r.get("offer_base_units") is None or (
            isinstance(r.get("offer_base_units"), int)
            and not isinstance(r.get("offer_base_units"), bool)
            and r.get("offer_asset")
            and isinstance(r.get("offer_decimals"), int)
        )
    )]
    check("offer-fields", not bad_offer,
          f"{len(bad_offer)} rows have offer_base_units without (int, asset, decimals) triple")

    usdc_str = [
        (i, k) for i, r in enumerate(rows)
        for k, v in r.items()
        if re.search(r"_usdc$", k) and isinstance(v, str)
    ]
    check("no-string-usdc-fields", not usdc_str,
          f"string values in *_usdc fields: {usdc_str[:5]}")

    # paid rows must carry a numeric payout
    paid_no_num = [r.get("id") for r in rows if r.get("status") == "paid"
                   and not isinstance(r.get("payout_usdc"), (int, float))]
    check("paid-rows-have-numeric-payout", not paid_no_num, f"{paid_no_num[:5]}")

    if errors:
        print(f"\n{len(errors)} CHECK(S) FAILED — DO NOT PUBLISH", file=sys.stderr)
        sys.exit(1)
    print("\nALL CHECKS PASS — safe to publish")


if __name__ == "__main__":
    main()
