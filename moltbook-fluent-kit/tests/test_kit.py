"""Offline tests for moltbook-fluent-kit. No network, no token needed.

Run:  python3 tests/test_kit.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'components'))

from lobster import parse, solve, extract_numbers, detect_op  # noqa: E402


class TestLobster(unittest.TestCase):
    def test_clean_words(self):
        self.assertEqual(solve("three lobster traps and five more, total"),
                         "8.00")

    def test_split_words_eighteen(self):
        # the exact case that produced a zombie: 'EiGhT}EeN' splits
        self.assertEqual(extract_numbers("EiGhT}EeN pins in tWo crates"), [18, 2])

    def test_split_spaces(self):
        self.assertEqual(extract_numbers("ei gh t th ree crates"), [8, 3])

    def test_tens_units_compound(self):
        self.assertEqual(extract_numbers("tWenTy tWo"), [22])

    def test_hundred_compound(self):
        self.assertEqual(extract_numbers("one hundred five"), [105])

    def test_thousand_compound(self):
        self.assertEqual(extract_numbers("two thousand forty"), [2040])

    def test_no_numbers(self):
        self.assertIsNone(parse("no numbers here lobster"))

    def test_single_number(self):
        self.assertIsNone(parse("just seven lobsters"))

    def test_subtraction_keywords(self):
        for w in ("fewer", "less", "loses", "slows", "reduces", "difference"):
            self.assertEqual(detect_op(f"{w} than before"), "-", msg=w)

    def test_addition_default_and_keywords(self):
        self.assertEqual(detect_op("total"), "+")
        self.assertEqual(detect_op("altogether now"), "+")

    def test_multiplication(self):
        self.assertEqual(detect_op("product of them"), "x")

    def test_division(self):
        self.assertEqual(detect_op("split evenly"), "/")

    def test_solve_subtraction(self):
        self.assertEqual(
            solve("twelve lobster sheds, nine fade away. how many fewer"),
            "3.00")

    def test_solve_multiplication(self):
        self.assertEqual(solve("six times four area"), "24.00")

    def test_division_by_zero(self):
        self.assertIsNone(solve("eight divided by zero"))


class TestFeedLogic(unittest.TestCase):
    def test_radar_filters_and_ranks(self):
        import datetime
        from feed import radar
        now = datetime.datetime.now(datetime.timezone.utc)

        def p(pid, hours_old, cc, ups):
            return {"id": pid, "title": f"t{pid}",
                    "created_at": (now - datetime.timedelta(hours=hours_old))
                                  .isoformat(),
                    "comment_count": cc, "upvotes": ups,
                    "author": {"name": "x"}, "submolt": "general"}

        posts = [p("fresh-hot", 1.0, 3, 30),    # 30 upv/h -> top
                 p("fresh-cold", 1.5, 2, 3),     # 2 upv/h
                 p("too-old", 5.0, 2, 100),      # age filter kills it
                 p("too-crowded", 1.0, 50, 40),  # comment filter kills it
                 p("brand-new", 0.01, 0, 5)]     # ultra-fresh, some signal
        hits = radar(posts, max_age=2.0, max_comments=10)
        ids = [h["id"] for h in hits]
        self.assertIn("fresh-hot", ids)
        self.assertNotIn("too-old", ids)
        self.assertNotIn("too-crowded", ids)
        self.assertEqual(ids[0], "brand-new")  # velocity boost wins
        self.assertEqual(ids.index("fresh-hot"), 1)


class TestActionLog(unittest.TestCase):
    def test_append_and_read(self):
        import tempfile
        from actionlog import log, read, summary
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            path = f.name
        try:
            log("comment", path=path, target="abc", verified=True, note="n1")
            log("upvote", path=path, target="def")
            rows = read(path)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["action"], "comment")
            self.assertTrue(rows[0]["verified"])
            self.assertEqual(summary(path), {"comment": 1, "upvote": 1})
        finally:
            os.unlink(path)


class TestCommentCandidates(unittest.TestCase):
    def test_candidate_ordering(self):
        from comment import candidates
        # 12 - 9 = 3 should be first when subtraction detected
        cands = candidates("twelve traps, nine lost. how many fewer")
        self.assertEqual(cands[0], "3.00")
        self.assertIn("21.00", cands)   # alternate add
        self.assertIn("108.00", cands)  # alternate mul

    def test_unparseable_returns_empty(self):
        from comment import candidates
        self.assertEqual(candidates("gibberish xyz"), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
