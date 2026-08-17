"""Component 5: actionlog.py — append-only audit trail for agent actions.

When an autonomous agent posts publicly under its operator's name, "what
did you do and why" must be answerable from a file, not from memory.
Every post/comment/upvote/follow appends one JSON line BEFORE the action
is counted as done. Mirrors the operator's own tx-log discipline.

Log format (JSONL, append-only):
  {"ts": ..., "action": "comment", "target": "<post_id>", "id": "<cid>",
   "verified": true, "note": "value-first, no links"}

Usage:
  from actionlog import log
  log("comment", target=post_id, id=cid, verified=True, note="...")

  python3 actionlog.py                  # tail 20
  python3 actionlog.py --summary        # counts by action
"""
from __future__ import annotations
import argparse
import datetime
import json
import os

DEFAULT_PATH = os.environ.get(
    "MFK_ACTIONLOG", os.path.expanduser("~/mfk-actions.jsonl"))


def log(action: str, path: str = DEFAULT_PATH, **fields) -> dict:
    entry = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "action": action, **fields}
    with open(path, 'a') as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def read(path: str = DEFAULT_PATH) -> list[dict]:
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path) if l.strip()]


def summary(path: str = DEFAULT_PATH) -> dict:
    counts: dict[str, int] = {}
    for e in read(path):
        counts[e.get("action", "?")] = counts.get(e.get("action", "?"), 0) + 1
    return counts


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--summary', action='store_true')
    ap.add_argument('--tail', type=int, default=20)
    a = ap.parse_args()
    if a.summary:
        for k, v in sorted(summary().items()):
            print(f"{k:12} {v}")
    else:
        rows = read()[-a.tail:]
        for e in rows:
            ok = "✓" if e.get("verified", True) else "✗"
            print(f"{e['ts'][:19]} {ok} {e.get('action'):8} "
                  f"{e.get('target', e.get('id', ''))[:12]:12} "
                  f"{e.get('note', '')[:60]}")
        if not rows:
            print("(empty log)")
