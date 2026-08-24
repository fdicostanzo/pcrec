#!/usr/bin/env python3
"""gen_expansions.py -- the assertion-family expansions, written as ORDINARY
lookaround patterns (sec 7.3's cheapest-source-of-non-invented-cells note,
and sec 2.1's "the constructs below are not a new surface -- they are the
vocabulary the assertions module is ALREADY written in").

la_d27_extract.md sec 6.1 (referenced, not seen directly -- this file's
patterns are written from the DEFINITIONS the D27 brief itself states in
its own THE TASK section, not recalled from sec 6.1's own text, which this
cell does not contain): `\\b` == `(?:(?<=\\w)(?!\\w)|(?<!\\w)(?=\\w))`,
`(?m)^` == `(?:\\A|(?<=\\n)(?!\\z))`, and by the same shape `(?m)$` ==
`(?:(?=\\n)|\\z)` -ish and `\\Z`'s optional-body lookahead form
`(?=\\n?\\z)`. This file writes the RHS lookaround expansions directly
(never the LHS shorthand, which is module `assertions`, not this one) and
tests them as patterns in their own right -- these are real lookaround
usages, not synthetic shapes, and per G7a they stay python-verifiable
(the width rule that would make a lookBEHIND reject `\\n?\\z` never
applies here because \\Z's own body sits in a lookAHEAD).

G7's own divergence (python's `\\Z` IS pcre2's `\\z`) is sidestepped
entirely: this file only ever writes `\\z` (never bare `\\Z`) inside a
lookaround body, matching pcre2's `\\z` and python's `\\Z` identically --
i.e. avoided by construction rather than marked, since \\z alone is
identical in both oracles.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import Block, RxtFile, pcre2_search, py_search, pcre2_ok, py_ok

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expansions.rxt")

# Each entry: (name, pattern, feats, subjects). Every pattern below is the
# RHS lookaround expansion of a real assertions-family construct, used
# here as an ordinary pattern under test -- never the \\b/\\Z/(?m)^ token
# itself, which belongs to module `assertions`.
CASES = [
    ("word-boundary (\\b)",
     r"a(?:(?<=\w)(?!\w)|(?<!\w)(?=\w))b",
     ["ab", "a b", "aab", "a.b", "..a.b..", " ab "]),
    ("multiline-^ ((?m)^)",
     r"(?:\A|(?<=\n)(?!\z))x",
     ["x", "\nx", "ax\n", "a\nx", "a\nxb", "\n\nx"]),
    ("end-of-subject-or-final-newline (\\Z's lookahead form)",
     r"a(?=\n?\z)",
     ["a", "a\n", "ab", "a\nb", "a\n\n"]),
    # \B is simply "not \b" -- since \b's own body is already zero-width,
    # wrapping it in a negative lookahead is a direct, safe De Morgan
    # negation rather than a second hand-derived expansion this blinded
    # author has no sec 6.1 access to check against.
    ("not-word-boundary (\\B, negation of \\b's own body)",
     r"a(?!(?:(?<=\w)(?!\w)|(?<!\w)(?=\w)))b",
     ["ab", "a b", "a1b", "aab"]),
]


def main():
    rf = RxtFile(OUT)
    for name, pat, subjects in CASES:
        assert pcre2_ok(pat), "expected pcre2 to accept %r (%s)" % (pat, name)
        py_okay = py_ok(pat)
        b = Block(pat, "lookaround")
        for s in subjects:
            r = pcre2_search(pat, s, 0)
            if r == "ERR":
                continue
            if r is None:
                b.n(s)
            else:
                span, groups = r
                b.m(s, span[0], span[1])
                for i, g in enumerate(groups, start=1):
                    b.g(i, g[0], g[1]) if g else b.gunset(i)
        # G7a: these stay python-verifiable, so `pcre2_only` should come
        # back False for every case here -- assert it, since a True here
        # would mean this file made exactly the G7a/G8-class mistake the
        # goal-facts list warns against.
        assert py_okay, "expansion %r (%s) unexpectedly not python-verifiable (G7a)" % (pat, name)
        rf.add(b, comment="assertion-family expansion: " + name, pcre2_only=False)

    header = (
        "# expansions.rxt -- [M6.6.3] D27 assertion-family expansions,\n"
        "# written as ORDINARY lookaround patterns (sec 2.1/sec 7.3). These\n"
        "# are the cheapest source of real, non-invented lookaround usage:\n"
        "# every one of these RHS expansions is what \\b/(?m)^/\\Z compile to\n"
        "# once the assertions module lands, so this file exercises this\n"
        "# module's own machinery under real-world shapes rather than\n"
        "# synthetic ones. G7a: these stay PYTHON-VERIFIABLE (asserted\n"
        "# above at generation time) -- the width rule that would refuse a\n"
        "# variable body never fires because the variable piece always\n"
        "# sits in a lookAHEAD, never a lookBEHIND.\n"
    )
    rf.write(header)
    print("expansions.rxt: %d blocks, %d cells, pcre2-only=%d python-verified=%d"
          % (rf.block_count(), rf.cell_count(), rf.pcre2only_count,
             rf.python_count))


if __name__ == "__main__":
    main()
