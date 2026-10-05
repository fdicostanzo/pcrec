"""[K82] (B) MAXIMUM-OFFSET SUBJECTS: random members of a pattern's language,
biased to its WIDEST spellings, for the handoff's differential and oracle.

The handoff's K is a bound on how far a match's run window sits from the
match's start; a K one byte too small deletes exactly the matches that use
the bound, and a random sweep over the pattern's alphabet almost never builds
one (`x{2,5}(?i)cat` needs five `x` then the run). So this generator walks
python's own parse of the pattern (`sre_parse`, the stdlib parser, so the
generator is not pcrec's walk) and emits members that take every repeat at
its MAXIMUM with probability 1/2, every class's widest UTF-8 member under
`-e utf8` (a 4-byte character for `.`, U+017F for a caseless `s`, U+212A for
a caseless `k`), and every alternation branch at random. Zero-width items
(anchors, assertions, back references) contribute nothing; a pattern python
cannot parse yields no members, and the caller says so.
"""
import random
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import sre_parse
    from sre_constants import (ANY, ASSERT, ASSERT_NOT, AT, BRANCH, CATEGORY,
                               CATEGORY_DIGIT, CATEGORY_NOT_DIGIT, CATEGORY_SPACE,
                               CATEGORY_NOT_SPACE, CATEGORY_WORD, CATEGORY_NOT_WORD,
                               GROUPREF, IN, LITERAL, MAX_REPEAT, MIN_REPEAT, NEGATE,
                               NOT_LITERAL, RANGE, SUBPATTERN, SRE_FLAG_IGNORECASE)

WIDE = ["\U0001F600", "€", "é", "a"]          # 4, 3, 2, 1 bytes
FOLD_WIDE = {"s": "ſ", "k": "K", "S": "ſ", "K": "K"}


def _lit(rnd, c, ic, utf8):
    ch = chr(c)
    if ic:
        opts = [ch.lower(), ch.upper()]
        if utf8 and ch in FOLD_WIDE and rnd.random() < 0.5:
            return FOLD_WIDE[ch]
        ch = rnd.choice(opts)
    return ch


def _cat(rnd, cat, utf8):
    return {CATEGORY_DIGIT: "7", CATEGORY_NOT_DIGIT: "é" if utf8 else "q",
            CATEGORY_SPACE: " ", CATEGORY_NOT_SPACE: "€" if utf8 else "q",
            CATEGORY_WORD: rnd.choice(["w", "_", "9"]),
            CATEGORY_NOT_WORD: "\U0001F600" if utf8 else "-"}.get(cat, "q")


def _in(rnd, items, ic, utf8):
    if items and items[0][0] is NEGATE:
        pool = WIDE if utf8 else ["\x7f", "~", "\xff"]
        bad = items[1:]
        for cand in pool + ["#", "!", "Z"]:
            if not any((op is LITERAL and ord(cand) == av) or
                       (op is RANGE and av[0] <= ord(cand) <= av[1]) for op, av in bad):
                return cand
        return pool[0]
    op, av = rnd.choice(items)
    if op is LITERAL:
        return _lit(rnd, av, ic, utf8)
    if op is RANGE:
        lo, hi = av
        c = hi if rnd.random() < 0.5 else rnd.randint(lo, hi)
        return _lit(rnd, c, ic, utf8)
    if op is CATEGORY:
        return _cat(rnd, av, utf8)
    return "q"


def _gen(rnd, seq, ic, utf8, out):
    for op, av in seq:
        if op is LITERAL:
            out.append(_lit(rnd, av, ic, utf8))
        elif op is NOT_LITERAL:
            out.append("€" if utf8 else ("q" if av != ord("q") else "z"))
        elif op is ANY:
            out.append((WIDE[0] if rnd.random() < 0.5 else rnd.choice(WIDE)) if utf8
                       else rnd.choice("a~\xe9"))
        elif op is IN:
            out.append(_in(rnd, av, ic, utf8))
        elif op is BRANCH:
            _gen(rnd, rnd.choice(av[1]), ic, utf8, out)
        elif op is SUBPATTERN:
            _gen(rnd, av[3], ic, utf8, out)
        elif op in (MAX_REPEAT, MIN_REPEAT):
            lo, hi, body = av
            top = hi if hi != sre_parse.MAXREPEAT else lo + 4
            n = min(top, 8) if rnd.random() < 0.5 else rnd.randint(lo, min(top, lo + 3))
            for _ in range(n):
                _gen(rnd, body, ic, utf8, out)
        elif op is CATEGORY:
            out.append(_cat(rnd, av, utf8))
        elif op in (AT, ASSERT, ASSERT_NOT, GROUPREF):
            pass


def members(pattern_bytes, utf8, n=24, seed=0x82B):
    """Up to `n` distinct members of the pattern's language, as bytes."""
    try:
        text = pattern_bytes.decode("utf-8" if utf8 else "latin-1")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = sre_parse.parse(text)
    except Exception:
        return []
    ic = bool(tree.state.flags & SRE_FLAG_IGNORECASE)
    rnd = random.Random(seed)
    out = set()
    for _ in range(n * 4):
        acc = []
        try:
            _gen(rnd, list(tree), ic, utf8, acc)
            s = "".join(acc).encode("utf-8" if utf8 else "latin-1")
        except (ValueError, UnicodeEncodeError, RecursionError):
            continue
        out.add(s)
        if len(out) >= n:
            break
    return sorted(out)
