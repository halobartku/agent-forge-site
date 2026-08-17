"""Component 1: lobster.py — solve Moltbook's lobster-math verification challenge.

The challenge arrives as obfuscated text (mixed case, braces, split words):
    "EiGhT}EeN lobster pins ... tWenTy}tWo ... how many fewer"
Numbers hide inside junk; the op hides in verbs ("fewer/loses" = subtract).

Parser strategy (hardened over ~20 real challenges, 12 zombie comments
taught us these lessons):
  1. strip non-alpha, lowercase, tokenize
  2. longest-first window merge for split words ("ei gh t" -> "eight")
  3. combine compounds: tens+units (twenty three -> 23),
     hundred/thousand + small (hundred five -> 105)
  4. op keywords decide + - x / (subtraction is the most common trap:
     'fewer/less/loses/slows/reduces' all mean minus)
"""
from __future__ import annotations
import re

WORD_NUMS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
    'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
    'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
    'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
    'hundred': 100, 'thousand': 1000,
}

SUB_WORDS = ('difference', 'subtract', 'less', 'minus', 'fewer', 'loses',
             'loss', 'lost', 'remaining', 'remain', 'decrease', 'drop',
             'drops', 'slows', 'slowed', 'reduces', 'reduced', 'reduce',
             'shrinks', 'decays', 'fades', 'weaken')
MUL_WORDS = ('times', 'multiply', 'product', 'multiplied', 'area')
DIV_WORDS = ('divided', 'split', 'quotient', 'ratio', 'average')
ADD_WORDS = ('total', 'sum', 'combined', 'altogether', 'plus', 'both',
             'gains', 'gain', 'added', 'add', 'increase')


def extract_numbers(text: str) -> list[int]:
    """All numbers in the challenge text, compounds merged."""
    cleaned = re.sub(r'[^a-z\s]', ' ', text.lower())
    tokens = [t for t in re.split(r'\s+', cleaned) if t]

    raw: list[int] = []
    i, n = 0, len(tokens)
    while i < n:
        matched = False
        # longest window first: catches "ei ght een"-style splits up to 4 tokens
        for w in range(min(4, n - i), 0, -1):
            cand = ''.join(tokens[i:i + w])
            if cand in WORD_NUMS:
                raw.append(WORD_NUMS[cand])
                i += w
                matched = True
                break
        if not matched:
            i += 1

    # merge compounds left-to-right (conservative — keeps distinct numbers
    # like [18, 2] separate):
    #   small before scale:  one hundred   -> 100, two thousand -> 2000
    #   scale absorbs rest:  two thousand forty -> 2040,
    #                        one hundred twenty three -> 123
    #   tens + units:        twenty three  -> 23
    vals: list[int] = []
    i = 0
    while i < len(raw):
        x = raw[i]
        nxt = raw[i + 1] if i + 1 < len(raw) else None
        if 1 <= x <= 9 and nxt in (100, 1000):        # "two thousand"
            base = x * nxt
            i += 2
            while i < len(raw) and 1 <= raw[i] < base:
                base += raw[i]; i += 1
            vals.append(base); continue
        if x in (100, 1000):                          # "hundred five"
            base = x
            i += 1
            while i < len(raw) and 1 <= raw[i] < base:
                base += raw[i]; i += 1
            vals.append(base); continue
        if 20 <= x < 100 and x % 10 == 0 and nxt is not None and 1 <= nxt <= 9:
            vals.append(x + nxt); i += 2; continue    # "twenty three"
        vals.append(x); i += 1
    return vals


def detect_op(text: str) -> str:
    cleaned = text.lower()
    if any(w in cleaned for w in SUB_WORDS):
        return '-'
    if any(w in cleaned for w in MUL_WORDS):
        return 'x'
    if any(w in cleaned for w in DIV_WORDS):
        return '/'
    return '+'  # default, and ADD_WORDS explicitly


def parse(text: str) -> tuple[int, str, int] | None:
    """(num1, op, num2) or None if unparseable."""
    nums = extract_numbers(text)
    if len(nums) < 2:
        return None
    return nums[0], detect_op(text), nums[1]


def solve(text: str) -> str | None:
    """Answer as the string the API expects: two-decimal fixed point."""
    p = parse(text)
    if not p:
        return None
    n1, op, n2 = p
    ans = {'+': n1 + n2, '-': n1 - n2, 'x': n1 * n2,
           '/': (n1 / n2) if n2 else None}.get(op)
    if ans is None:
        return None
    return f"{ans:.2f}"


if __name__ == '__main__':
    import sys
    print(solve(' '.join(sys.argv[1:])) or 'UNSOLVABLE')
