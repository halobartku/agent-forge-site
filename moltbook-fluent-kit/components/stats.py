"""Component 4: stats.py — karma / comment reconciliation tracker.

Sprint rule: a comment that isn't `verified` does not exist. There is no
/me endpoint on the API, so truth is assembled from the threads you've
touched (per the action log) plus the feed:

  - comments you THINK you posted vs. comments actually visible
  - pending/failed zombies found on your threads (delete them!)
  - per-comment score (is your style landing?)

Usage:
  python3 stats.py [post_id ...]        # default: threads in action log
  python3 stats.py --clean              # also DELETE non-verified comments
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(__file__))
from actionlog import DEFAULT_PATH, read as read_log  # noqa: E402

BASE = "https://www.moltbook.com/api/v1"
TOKEN = os.environ.get("MOLTBOOK_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
MY_NAME = os.environ.get("MOLTBOOK_NAME", "hermespnl")


def threads_from_log() -> list[str]:
    ids = []
    for e in read_log():
        t = e.get("target", "")
        if t and t not in ids:
            ids.append(t)
    return ids


def fetch_comments(post_id: str) -> list[dict]:
    r = requests.get(f"{BASE}/posts/{post_id}/comments",
                     headers=HEADERS, timeout=30).json()
    # API soft-deletes: is_deleted comments stay in listings forever.
    # They are gone from readers' view — treat them as nonexistent.
    return [c for c in r.get("comments", [])
            if c.get("author", {}).get("name") == MY_NAME
            and not c.get("is_deleted")]


def resolve_ids(post_ids: list[str]) -> list[str]:
    """Expand short id prefixes to full ids via the feed (the API silently
    returns empty for short ids instead of 404)."""
    need = [p for p in post_ids if len(p) < 32]
    if not need:
        return post_ids
    feed = requests.get(f"{BASE}/feed?limit=100",
                        headers=HEADERS, timeout=30).json().get("posts", [])
    out = []
    for p in post_ids:
        if len(p) >= 32:
            out.append(p)
            continue
        m = [f["id"] for f in feed if f["id"].startswith(p)]
        out.extend(m[:1])  # prefixes are unambiguous in practice
    return [p for p in out if p]


def reconcile(post_ids: list[str], clean: bool = False) -> dict:
    verified, zombies = [], []
    post_ids = resolve_ids(post_ids)
    for pid in post_ids:
        for c in fetch_comments(pid):
            st = c.get("verification_status")
            if st == "verified":
                verified.append(c)
            else:
                zombies.append(c)
                if clean:
                    requests.delete(f"{BASE}/comments/{c['id']}",
                                    headers=HEADERS, timeout=30)
    return {
        "posts_scanned": len(post_ids),
        "comments_verified": len(verified),
        "score_total": sum(c.get("score", 0) or 0 for c in verified),
        "best_comment": max((c.get("score", 0) or 0 for c in verified),
                            default=0),
        "zombies": [{"id": c["id"], "status": c.get("verification_status")}
                    for c in zombies],
        "zombies_deleted": len(zombies) if clean else 0,
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('post_ids', nargs='*')
    ap.add_argument('--clean', action='store_true',
                    help='delete non-verified comments found')
    a = ap.parse_args()
    pids = a.post_ids or threads_from_log()
    if not pids:
        sys.exit("no post ids given and action log empty")
    res = reconcile(pids, a.clean)
    print(json.dumps(res, indent=2))
    if res["zombies"] and not a.clean:
        print("\n⚠ zombies found — run with --clean to delete them")
