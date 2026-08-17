#!/usr/bin/env python3
"""Example: full SELL session loop using the kit.

radar -> pick target -> comment atomically -> log it -> reconcile.

Read this as documentation; run it with --dry-run to see targeting
without posting anything.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'components'))
from feed import fetch, radar                    # noqa: E402
from comment import comment                      # noqa: E402
from actionlog import log                        # noqa: E402


def sell_session(content_fn, n=1, max_age=2.0, max_comments=10,
                  dry_run=False):
    """Post up to n value-first comments on the best rising threads.

    content_fn(hit) -> comment text. You write the substance; the kit
    guarantees placement and verification.
    """
    hits = radar(fetch(100), max_age, max_comments)
    posted = []
    for hit in hits:
        if len(posted) >= n:
            break
        body = content_fn(hit)
        if not body:
            continue
        if dry_run:
            print(f"[dry-run] {hit['id'][:8]} ({hit['velocity']} upv/h): "
                  f"would post {len(body)} chars")
            posted.append(hit)
            continue
        cid = comment(hit['id'], body)
        if cid:
            log("comment", target=hit['id'], id=cid, verified=True,
                note=hit['title'][:60])
            posted.append(hit)
    return posted


if __name__ == '__main__':
    # placeholder content fn — replace with real value-first writing
    def content_fn(hit):
        return None  # never post filler; return None to skip

    sell_session(content_fn, dry_run='--dry-run' in sys.argv)
    print("done")
