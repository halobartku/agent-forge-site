#!/usr/bin/env bash
# receipt-card self-test: mint → verify → tamper-detect → list
set -e
cd "$(dirname "$0")/.."
export RECEIPT_CARD_DIR=$(mktemp -d)/receipts
export RECEIPT_CARD_SECRET=$(mktemp -d)/secret.key
R=$(python3 receipt_card.py mint --tx 0xselftest --deliverable selftest.tar.gz --amount 1.00 --payer selftest | grep -oP '(?<=: ).*receipt-.*\.json')
python3 receipt_card.py verify --receipt "$R" > /dev/null
python3 - "$R" <<'EOF'
import json, sys
p = sys.argv[1]
r = json.load(open(p)); r["amount"] = 999.0; json.dump(r, open(p, "w"))
EOF
if python3 receipt_card.py verify --receipt "$R" > /dev/null 2>&1; then
  echo "FAIL: tamper not detected"; exit 1
else
  echo "PASS: mint+verify+tamper-detect"
fi
