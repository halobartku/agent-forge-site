"""Component 3: feed.py — fresh-thread radar.

Comment karma on Moltbook is a placement game. A great comment in a
1000-comment thread is invisible; the same comment in a 2-hour-old thread
with 4 comments rides the top of the thread all day.

Radar rules (tuned during the sprint):
  - age < 2h        : still climbing /hot, commenters get read
  - comments < 10   : you're early enough to be top-3
  - sort by upvote velocity (upvotes/hour), not raw score

Usage:
  python3 feed.py [--max-age 2] [--max-comments 10] [--limit 100] [--json]
"""
from __future__ import annotations
import argparse
import datetime
import json
import os
import requests

BASE = "https://www.moltbook.com/api/v1"
TOKEN = os.environ.get("MOLTBOOK_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def _age_hours(iso: str, now) -> float:
    try:
        t = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (now - t).total_seconds() / 3600
    except Exception:
        return -1.0


def fetch(limit: int = 100, submolt: str | None = None) -> list[dict]:
    url = f"{BASE}/feed?limit={limit}"
    if submolt:
        url += f"&submolt={submolt}"
    return requests.get(url, headers=HEADERS, timeout=30).json().get("posts", [])


def radar(posts: list[dict], max_age: float = 2.0,
          max_comments: int = 10) -> list[dict]:
    """Filter + rank posts by comment-opportunity score."""
    now = datetime.datetime.now(datetime.timezone.utc)
    hits = []
    for p in posts:
        age = _age_hours(p.get("created_at", ""), now)
        if age < 0 or age > max_age:
            continue
        cc = p.get("comment_count", 0)
        if cc > max_comments:
            continue
        ups = p.get("upvotes", 0)
        v = ups / age if age > 0.05 else ups * 20  # very fresh -> high velocity
        hits.append({"id": p["id"], "title": p.get("title", ""),
                     "author": p.get("author", {}).get("name", "?"),
                     "age_h": round(age, 2), "comments": cc,
                     "upvotes": ups, "velocity": round(v, 1),
                     "submolt": p.get("submolt", "")})
    hits.sort(key=lambda h: h["velocity"], reverse=True)
    return hits


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-age', type=float, default=2.0)
    ap.add_argument('--max-comments', type=int, default=10)
    ap.add_argument('--limit', type=int, default=100)
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    hits = radar(fetch(a.limit), a.max_age, a.max_comments)
    if a.json:
        print(json.dumps(hits, indent=2))
    else:
        for h in hits:
            print(f"{h['velocity']:>7} | {h['age_h']:>5}h | c:{h['comments']:<3}"
                  f" | u:{h['upvotes']:<4} | {h['id']} "
                  f"| r/{h['submolt'] or '-'} | {h['title'][:60]}")
        if not hits:
            print("(no fresh threads match — widen --max-age)")
