#!/usr/bin/env python3
"""gen_longsubject.py -- sec 10.1 population requirement 3: the corpus
MUST contain a LONG-SUBJECT LEADING multi-branch lookbehind (R33 C1-6),
or sec 3.7's n*sum(k_i) work-charge shape is reasoned about and never
measured, and it is the one shape that can reach PCREC_ERR_WORK where
PCRE2 matches.

"Leading multi-branch lookbehind" -- a lookbehind with several
DIFFERENT-fixed-width branches (so the fixed-per-branch rule ships it),
sitting at a position the matcher must scan FORWARD across a long subject
to reach, so the back-step machine runs once per candidate position over
the whole scan, not just once at a lucky early hit.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import Block, RxtFile, pcre2_search, py_search, pcre2_ok, py_ok

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "longsubject.rxt")

# Four branches of different fixed widths (1, 2, 3, 4) -- sec 3.7's
# n*sum(k_i) shape wants several DIFFERENT k_i, not just two.
PAT = r"(?<=a|bb|ccc|dddd)X"


def make_subject(n_junk, hit_branch, tail_after=0):
    """A subject of `n_junk` filler bytes (none of which end in a branch
    match immediately before an 'X'), then one of the four branches
    immediately followed by 'X', then `tail_after` more filler bytes (so
    the 'X' is not conveniently the last byte of the subject either)."""
    filler = "e" * n_junk
    branch = {1: "a", 2: "bb", 3: "ccc", 4: "dddd"}[hit_branch]
    return filler + branch + "X" + "e" * tail_after


def main():
    rf = RxtFile(OUT)
    assert pcre2_ok(PAT)
    py_okay = py_ok(PAT)

    b = Block(PAT, "lookaround")
    cases = []
    # Long leading run (300 bytes) of NON-matching filler before the hit,
    # once per branch width, so the back-step machine is exercised at
    # every candidate position across a genuinely long scan.
    for width in (1, 2, 3, 4):
        cases.append(make_subject(300, width, tail_after=0))
    # A long run where the hit is near the START (cheap positive control)
    cases.append(make_subject(0, 4, tail_after=300))
    # A long subject with NO hit at all (worst case for the scan -- every
    # position across 300+ bytes gets tried and rejected).
    cases.append("e" * 400)
    # A long subject where a NEAR-MISS almost-branch sits right before
    # 'X' repeatedly (partial branch prefixes that must not falsely hit):
    # 'c','cc' (short of "ccc"), 'ddd' (short of "dddd"), each followed by
    # a stray 'X' that must NOT match.
    near_miss = "e" * 100 + "cX" + "e" * 50 + "ccX" + "e" * 50 + "dddX" + "e" * 100
    cases.append(near_miss)

    for s in cases:
        r = pcre2_search(PAT, s, 0)
        if r is None:
            b.n(s)
        else:
            span, groups = r
            b.m(s, span[0], span[1])
    rf.add(b, comment="sec 10.1 requirement 3 (R33 C1-6): a long-subject "
           "leading multi-branch lookbehind, four DIFFERENT fixed widths, "
           "exercising sec 3.7's n*sum(k_i) work-charge shape across a "
           "300+ byte scan -- the one shape that can reach PCREC_ERR_WORK "
           "where PCRE2 matches.", pcre2_only=not py_okay)

    # A second block: the SAME shape but with startpos > 0, combining
    # requirement 3 with requirement 2 (ms/ns over a lookbehind) in one
    # cell -- the lookbehind must still be able to read bytes between 0
    # and startpos across a long leading run.
    b2 = Block(PAT, "lookaround")
    long_subj = "e" * 300 + "ccc" + "X" + "e" * 50
    p0 = 303  # position of 'X'
    r = pcre2_search(PAT, long_subj, p0)
    if r is None:
        b2.ns(p0, long_subj)
    else:
        span, groups = r
        b2.ms(p0, long_subj, span[0], span[1])
    # And the SAME string searched from startpos 0 (unanchored scan must
    # reach the same hit by forward search rather than starting there).
    r0 = pcre2_search(PAT, long_subj, 0)
    if r0 is None:
        b2.n(long_subj)
    else:
        span, groups = r0
        b2.m(long_subj, span[0], span[1])
    rf.add(b2, comment="requirement 3 x requirement 2 combined: long "
           "leading multi-branch lookbehind, both from startpos 0 (forward "
           "scan) and from startpos placed exactly at the hit.",
           pcre2_only=not py_okay)

    header = (
        "# longsubject.rxt -- [M6.6.3] D27 corpus, sec 10.1 population\n"
        "# requirement 3 (R33 C1-6): a long-subject leading multi-branch\n"
        "# lookbehind. Without a block like this, sec 3.7's work-charge\n"
        "# shape is reasoned about and never measured.\n"
    )
    rf.write(header)
    print("longsubject.rxt: %d blocks, %d cells, pcre2-only=%d python-verified=%d"
          % (rf.block_count(), rf.cell_count(), rf.pcre2only_count,
             rf.python_count))


if __name__ == "__main__":
    main()
