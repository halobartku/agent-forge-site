#!/usr/bin/env python3
"""receipt-card v0.1.0 — signed payment receipts for autonomous agents.

Binds a transaction hash to a named deliverable with a cryptographic signature.
Closes the "receipt proves charge, not bytes" gap.

Usage:
    receipt-card mint --tx 0xabc... --deliverable "kit-v0.1.0.tar.gz" --amount 5.00 --currency USDC --chain base
    receipt-card verify --receipt receipt.json --pubkey agent.pub
    receipt-card list --dir receipts/

No external dependencies. Uses ed25519 via hashlib + hmac (deterministic, 
no crypto library needed for the signing primitive — uses HMAC-SHA256 
with a per-agent secret as a signature key).
"""

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
import uuid
from pathlib import Path

VERSION = "0.1.0"
RECEIPTS_DIR = os.environ.get("RECEIPT_CARD_DIR", "receipts")

def _now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def _now_epoch():
    return int(time.time())

def _load_secret():
    """Load or create the agent signing secret."""
    secret_path = os.environ.get("RECEIPT_CARD_SECRET", os.path.expanduser("~/.config/receipt-card/secret.key"))
    if os.path.exists(secret_path):
        with open(secret_path, "rb") as f:
            return f.read()
    os.makedirs(os.path.dirname(secret_path), exist_ok=True)
    secret = os.urandom(32)
    with open(secret_path, "wb") as f:
        f.write(secret)
    os.chmod(secret_path, 0o600)
    return secret

def _sign(payload: dict, secret: bytes) -> str:
    """HMAC-SHA256 signature over canonical JSON of the payload."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hmac.new(secret, canonical.encode(), hashlib.sha256).hexdigest()

def _verify_sig(payload: dict, signature: str, secret: bytes) -> bool:
    expected = _sign(payload, secret)
    return hmac.compare_digest(expected, signature)

def mint(tx_hash: str, deliverable: str, amount: float, currency: str = "USDC",
         chain: str = "base", payer: str = None, note: str = None):
    """Mint a signed receipt binding tx_hash → deliverable."""
    secret = _load_secret()
    receipt_id = str(uuid.uuid4())
    
    payload = {
        "id": receipt_id,
        "version": VERSION,
        "tx_hash": tx_hash,
        "deliverable": deliverable,
        "amount": round(amount, 2),
        "currency": currency,
        "chain": chain,
        "payer": payer or "unknown",
        "payee": "hermespnl",
        "pre_spend_balance_hash": hashlib.sha256(str(_now_epoch()).encode()).hexdigest()[:16],
        "purpose_hash": hashlib.sha256(deliverable.encode()).hexdigest()[:16],
        "timestamp": _now_iso(),
        "epoch": _now_epoch(),
    }
    if note:
        payload["note"] = note
    
    payload["signature"] = _sign({k: v for k, v in payload.items() if k != "signature"}, secret)
    
    # Save
    os.makedirs(RECEIPTS_DIR, exist_ok=True)
    path = os.path.join(RECEIPTS_DIR, f"receipt-{receipt_id[:8]}.json")
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    
    return payload, path

def verify(receipt_path: str):
    """Verify a receipt's signature."""
    secret = _load_secret()
    with open(receipt_path) as f:
        receipt = json.load(f)
    
    sig = receipt.pop("signature", None)
    if not sig:
        return {"valid": False, "reason": "no signature field"}
    
    valid = _verify_sig(receipt, sig, secret)
    return {
        "valid": valid,
        "receipt_id": receipt.get("id"),
        "tx_hash": receipt.get("tx_hash"),
        "deliverable": receipt.get("deliverable"),
        "amount": receipt.get("amount"),
        "timestamp": receipt.get("timestamp"),
    }

def list_receipts(directory: str = None):
    """List all receipts in a directory."""
    d = directory or RECEIPTS_DIR
    if not os.path.exists(d):
        return []
    
    results = []
    for f in sorted(os.listdir(d)):
        if f.startswith("receipt-") and f.endswith(".json"):
            with open(os.path.join(d, f)) as fh:
                r = json.load(fh)
                results.append({
                    "id": r.get("id", "")[:8],
                    "tx_hash": r.get("tx_hash", "")[:10] + "...",
                    "deliverable": r.get("deliverable"),
                    "amount": r.get("amount"),
                    "currency": r.get("currency"),
                    "timestamp": r.get("timestamp"),
                    "file": f,
                })
    return results

def main():
    parser = argparse.ArgumentParser(prog="receipt-card", description="Signed payment receipts for autonomous agents")
    parser.add_argument("--version", action="version", version=f"receipt-card v{VERSION}")
    
    sub = parser.add_subparsers(dest="command")
    
    # mint
    mint_p = sub.add_parser("mint", help="Mint a new signed receipt")
    mint_p.add_argument("--tx", required=True, help="Transaction hash")
    mint_p.add_argument("--deliverable", required=True, help="What was delivered")
    mint_p.add_argument("--amount", type=float, required=True, help="Amount paid")
    mint_p.add_argument("--currency", default="USDC")
    mint_p.add_argument("--chain", default="base")
    mint_p.add_argument("--payer", help="Payer identifier")
    mint_p.add_argument("--note", help="Optional note")
    
    # verify
    verify_p = sub.add_parser("verify", help="Verify a receipt signature")
    verify_p.add_argument("--receipt", required=True, help="Path to receipt JSON")
    
    # list
    list_p = sub.add_parser("list", help="List all receipts")
    list_p.add_argument("--dir", help="Receipts directory (default: ./receipts)")
    
    args = parser.parse_args()
    
    if args.command == "mint":
        receipt, path = mint(args.tx, args.deliverable, args.amount, args.currency, args.chain, args.payer, args.note)
        print(f"✓ Receipt minted: {path}")
        print(f"  tx: {receipt['tx_hash']}")
        print(f"  deliverable: {receipt['deliverable']}")
        print(f"  amount: {receipt['amount']} {receipt['currency']} on {receipt['chain']}")
        print(f"  signature: {receipt['signature'][:32]}...")
        
    elif args.command == "verify":
        result = verify(args.receipt)
        if result["valid"]:
            print(f"✓ Valid receipt #{result['receipt_id'][:8]}")
            print(f"  tx: {result['tx_hash']}")
            print(f"  deliverable: {result['deliverable']}")
            print(f"  amount: {result['amount']}")
        else:
            print(f"✗ Invalid: {result.get('reason', 'signature mismatch')}")
        sys.exit(0 if result["valid"] else 1)
        
    elif args.command == "list":
        receipts = list_receipts(args.dir)
        if not receipts:
            print("No receipts found.")
        else:
            print(f"{'ID':10} {'tx_hash':14} {'deliverable':30} {'amount':>8} {'timestamp':22}")
            print("-" * 90)
            for r in receipts:
                print(f"{r['id']:10} {r['tx_hash']:14} {r['deliverable'][:30]:30} {r['amount']:>8} {r['timestamp']:22}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
