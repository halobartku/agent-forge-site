"""Component 2: comment.py — atomic comment: post -> solve -> verify.

The #1 silent killer on Moltbook is the zombie comment: you post, the API
returns a verification challenge, your session dies before solving it, and
the comment sits `pending` FOREVER — invisible, undeletable-by-default,
counted as a win in your own logs but seen by no one. 12 of our first 17
comments died this way.

This component makes the whole flow atomic:
  - one attempt = post + solve + verify
  - wrong answer burns the single-use code -> delete + re-post (fresh code)
  - unparseable challenge -> delete immediately
  - only returns True on verification_status == verified

Usage:
  python3 comment.py <post_id> <text | @file.txt> [--retries N]
"""
from __future__ import annotations
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(__file__))
from lobster import parse  # noqa: E402

BASE = "https://www.moltbook.com/api/v1"
TOKEN = os.environ.get("MOLTBOOK_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}",
           "Content-Type": "application/json"}


def candidates(text: str) -> list[str]:
    """Ordered candidate answers: best parse first, alternates behind."""
    p = parse(text)
    if not p:
        return []
    n1, op, n2 = p
    primary = {'+': n1 + n2, '-': n1 - n2, 'x': n1 * n2}
    ordered = []
    if op in primary:
        ordered.append(primary[op])
    for v in primary.values():
        if v not in ordered:
            ordered.append(v)
    if n2:
        ordered.append(n1 / n2)
    out = []
    for c in ordered:
        if c >= 0 and f"{c:.2f}" not in out:
            out.append(f"{c:.2f}")
    return out


def post_comment(post_id: str, content: str) -> dict:
    r = requests.post(f"{BASE}/posts/{post_id}/comments",
                      headers=HEADERS, json={"content": content}, timeout=30)
    r.raise_for_status()
    return r.json()


def delete_comment(cid: str) -> None:
    requests.delete(f"{BASE}/comments/{cid}", headers=HEADERS, timeout=30)


def verify(code: str, answer: str) -> dict:
    r = requests.post(f"{BASE}/verify", headers=HEADERS,
                      json={"verification_code": code, "answer": answer},
                      timeout=30)
    return r.json()


def comment(post_id: str, content: str, retries: int = 4,
            verbose: bool = True) -> str | None:
    """Post a comment and guarantee it ends verified or not at all.

    Returns the comment id on success, None on failure. Never leaves a
    pending zombie behind.
    """
    for attempt in range(1, retries + 1):
        resp = post_comment(post_id, content)
        if not resp.get("success"):
            if verbose:
                print(f"post-fail: {str(resp)[:200]}")
            return None
        c = resp.get("comment", {})
        cid = c.get("id")
        v = c.get("verification") or resp.get("verification") or {}
        if not v:  # no challenge issued
            ok = c.get("verification_status") == "verified"
            if verbose:
                print(f"no challenge (status={c.get('verification_status')})")
            return cid if ok else None
        cands = candidates(v.get("challenge_text", ""))
        if verbose:
            print(f"attempt {attempt}: {cands[:4]}")
        if not cands:
            delete_comment(cid)
            continue
        # code is single-use: exactly ONE answer per posted challenge
        vr = verify(v.get("verification_code", ""), cands[0])
        if vr.get("success"):
            if verbose:
                print(f"VERIFIED {cid[:8]}")
            return cid
        delete_comment(cid)
        if verbose:
            print(f"rejected '{cands[0]}', retrying with fresh challenge")
    return None


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    retries = 4
    for a in sys.argv[1:]:
        if a.startswith('--retries'):
            retries = int(a.split('=')[1])
    pid, body = args[0], args[1]
    if body.startswith('@'):
        body = open(body[1:]).read()
    sys.exit(0 if comment(pid, body.strip(), retries) else 1)
