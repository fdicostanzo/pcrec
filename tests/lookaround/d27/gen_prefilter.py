#!/usr/bin/env python3
"""gen_prefilter.py -- sec 10.1 population requirement 1: the corpus MUST
contain one of sec 5.5's 16 qualifying shapes (a lookaround inside an
alternation with a bounded-repeat, mandatory-tail follow), or S-LA12
cannot go red. The extract names the measured witness verbatim:
`((?:a(?!q)|aq)(?:xy){0,4}q)` on "aqq".

This file uses that exact witness plus a handful of oracle-mined
neighbours (same shape family, different subjects/bounds) so the cell is
not a single hard-coded line an unrelated edit could silently orphan.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import Block, RxtFile, pcre2_search, py_search, pcre2_ok, py_ok

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prefilter.rxt")

PATTERNS = [
    r"((?:a(?!q)|aq)(?:xy){0,4}q)",
    r"((?:a(?!q)|aq)(?:xy){0,4}q)",  # same pattern, wider subject sweep below
    r"((?:a(?!b)|ab)(?:cd){0,3}b)",
]

SUBJECTS_BY_INDEX = [
    ["aqq", "aq", "aqxyq", "aqxyxyq", "aqxyxyxyxyq", "aaqq", "aqxyxyxyxyxyq"],
    ["q", "aqxyxyxyq", "aqxyxyxyxyxyxyq", ""],
    ["ab", "abb", "abcdb", "abcdcdb", "abcdcdcdcdb", "aab", "abcdcdcdcdcdb"],
]


def main():
    rf = RxtFile(OUT)
    for pat, subjects in zip(PATTERNS, SUBJECTS_BY_INDEX):
        assert pcre2_ok(pat), "expected pcre2 to accept %r" % (pat,)
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
        rf.add(b, comment="sec 10.1 requirement 1 (S-LA12/sec 5.5 prefilter "
               "witness): a lookaround inside an alternation with a "
               "bounded-repeat, mandatory-tail follow.",
               pcre2_only=not py_okay)

    header = (
        "# prefilter.rxt -- [M6.6.3] D27 corpus, sec 10.1 population\n"
        "# requirement 1 (S-LA12/sec 5.5's qualifying shape). Without a\n"
        "# block like this the prefilter sabotage cannot go red at all.\n"
        "# The primary cell is la_d27_extract.md's own measured witness,\n"
        "# `((?:a(?!q)|aq)(?:xy){0,4}q)` on \"aqq\", verbatim.\n"
    )
    rf.write(header)
    print("prefilter.rxt: %d blocks, %d cells, pcre2-only=%d python-verified=%d"
          % (rf.block_count(), rf.cell_count(), rf.pcre2only_count,
             rf.python_count))


if __name__ == "__main__":
    main()
