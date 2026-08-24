#!/usr/bin/env python3
"""gen_adversarial.py -- deliberately hand-targeted cells: what would a
lowering that forgot to restore the cursor, forgot to cut, cut on the
wrong arm, scoped the follow wrongly, mis-measured a branch width, or
clamped the lookbehind to the search-start answer differently. Also
carries sec 10.1 population requirement 4 (empty capture inside a
lookaround; a re-entered group across one).

Every cell's expectation is still an oracle read, never a guess -- the
"adversarial" part is entirely in WHICH pattern/subject pairs were chosen,
not in how the expectation was derived.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import Block, RxtFile, pcre2_search, py_search, pcre2_ok, py_ok

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adversarial.rxt")


def emit(rf, pat, feats, subjects, comment, starts=None):
    """subjects: list of subject strings (start=0), OR if `starts` is
    given, a list of (subject, start) pairs (mix of m/n and ms/ns)."""
    assert pcre2_ok(pat), "expected pcre2 to accept %r" % (pat,)
    py_okay = py_ok(pat)
    b = Block(pat, feats)
    pairs = starts if starts is not None else [(s, 0) for s in subjects]
    for s, p in pairs:
        r = pcre2_search(pat, s, p)
        if r == "ERR":
            continue
        if p == 0:
            if r is None:
                b.n(s)
            else:
                span, groups = r
                b.m(s, span[0], span[1])
                for i, g in enumerate(groups, start=1):
                    b.g(i, g[0], g[1]) if g else b.gunset(i)
        else:
            if r is None:
                b.ns(p, s)
            else:
                span, groups = r
                b.ms(p, s, span[0], span[1])
                for i, g in enumerate(groups, start=1):
                    b.g(i, g[0], g[1]) if g else b.gunset(i)
    rf.add(b, comment=comment, pcre2_only=not py_okay)


def main():
    rf = RxtFile(OUT)

    # -----------------------------------------------------------------
    # (1) Cut on the WRONG ARM -- the brief's own example. A lowering
    # that let the outer a+ share backtrack state with the inner (a+)
    # inside the negative lookahead (instead of scoping the cut to the
    # assertion body only) could wrongly conclude this MATCHES.
    # -----------------------------------------------------------------
    emit(rf, r"(?!(a+)b)a+b", "lookaround",
         ["aab", "ab", "aaab", "b"],
         "ADVERSARIAL: cut-on-wrong-arm. (?!(a+)b)a+b on \"aab\" must be "
         "NOMATCH (the brief's own named trap) -- a wrong lowering that "
         "lets the outer a+ inherit backtrack positions the inner "
         "lookahead's (a+) already tried would wrongly match.")

    # -----------------------------------------------------------------
    # (2) Forgot to RESTORE THE CURSOR after a lookbehind -- the
    # continuation must resume from the position immediately after the
    # lookbehind's zero-width assertion, not from wherever the body's
    # internal forward-simulated scan left off. Multi-group body so a
    # restore bug that only resets ONE state variable (position but not
    # captures, or captures but not position) is still caught.
    # -----------------------------------------------------------------
    emit(rf, r"(?<=(a)(b))(c)(d)", "lookaround",
         ["abcd", "xabcd", "abcde"],
         "ADVERSARIAL: cursor-restore. Groups 1/2 come from INSIDE the "
         "lookbehind (must be retained per sec 2.5's capture rule) while "
         "groups 3/4 come from AFTER it and must see the position exactly "
         "where the lookbehind assertion ended, not mid-body.")

    # -----------------------------------------------------------------
    # (3) Forgot to CUT (atomicity) on a greedy backref chain -- an
    # atomic lookahead capturing greedily, then a backref that could only
    # succeed by the atomic group re-trying a shorter match.
    # -----------------------------------------------------------------
    emit(rf, r"(?=(a+))\1b", "lookaround,backrefs",
         ["aaab", "aaaab", "ab", "aab"],
         "ADVERSARIAL: forgot-to-cut. (?=(a+))\\1b on greedy runs of 'a' -- "
         "the atomic lookahead takes the MAXIMAL run and \\1 must match "
         "that exact (non-backtracked) run before 'b'; a lowering that let "
         "the lookahead's a+ retry shorter would falsely succeed on "
         "subjects where only a shorter \\1 plus 'b' fits.")

    # -----------------------------------------------------------------
    # (4) SCOPED THE FOLLOW WRONGLY -- chained lookarounds where what
    # comes after the SECOND assertion must be checked from the position
    # after BOTH (both zero-width, so still the original position), not
    # from some intermediate state either assertion's body computed.
    # -----------------------------------------------------------------
    emit(rf, r"(?=a)(?=(a))\1b", "lookaround,backrefs",
         ["ab", "a", "b"],
         "ADVERSARIAL: follow-scoping. Two chained lookaheads before a "
         "backref+literal continuation -- the continuation must see the "
         "ORIGINAL position (both assertions are zero-width), not a "
         "position either assertion's internal body scan advanced to.")

    # -----------------------------------------------------------------
    # (5) MIS-MEASURED A BRANCH WIDTH -- boundary cells between the SHIP
    # (fixed-per-branch, different widths ok) and REFUSE (any branch
    # bounded/unbounded variable) rule, immediately adjacent in shape so
    # an off-by-one in the min==max check would flip one but not the
    # other. These are SHIP cells (unlike refusals.rxt's REFUSE-side
    # boundary cells) -- both sides of the boundary belong in the corpus.
    # -----------------------------------------------------------------
    emit(rf, r"(?<=a{3}|bb)x", "lookaround",
         ["aaax", "bbx", "aax", "bx", "x"],
         "ADVERSARIAL: branch-width boundary (SHIP side). An EXACT "
         "quantifier a{3} is fixed width 3 -- must ship, not be confused "
         "with a bounded-VARIABLE quantifier of the same max.")
    emit(rf, r"(?<=(?:a{2})|(?:a{3}))x", "lookaround",
         ["aax", "aaax", "ax", "x"],
         "ADVERSARIAL: branch-width boundary (SHIP side), composite "
         "grouped branches -- widths 2 and 3, computed through a nested "
         "non-capturing group rather than read off a flat alternation.")

    # -----------------------------------------------------------------
    # (6) CLAMPED THE LOOKBEHIND TO SEARCH-START differently -- the
    # sharpest ms/ns cell in the corpus: a lookbehind whose body reads
    # bytes STRICTLY BEFORE startpos (not merely before the eventual
    # match position, which is the easy case gen_matrix.py's ms cells
    # already cover from a different angle). A wrong clamp that treats
    # startpos like `^` (an absolute floor the lookbehind cannot read
    # below) reports NOMATCH here where the correct answer is MATCH.
    # -----------------------------------------------------------------
    emit(rf, r"(?<=abc)x", "lookaround",
         [],
         "ADVERSARIAL: lookbehind-vs-startpos clamp. (?<=abc)x on \"abcx\" "
         "searched from startpos=3 MUST MATCH (3,4) -- the lookbehind reads "
         "bytes [0,3) which are entirely BEFORE startpos, exactly sec 3.8's "
         "contract (\"a lookbehind reads subject bytes before startpos\"). "
         "A wrong clamp that treats startpos as an absolute floor (like ^) "
         "would wrongly answer NOMATCH here. The startpos=4 cell is the "
         "boundary control (no 'x' left to match, unrelated to the clamp); "
         "\"zzzabcx\" from startpos=3 is the same shape with real bytes "
         "sitting even further before startpos.",
         starts=[("abcx", 3), ("abcx", 4), ("zzzabcx", 3)])

    # A second, deliberately narrower clamp cell: startpos placed so that
    # EXACTLY the bytes the lookbehind needs are available before it and
    # not one more -- the tightest version of the same trap, plus its
    # one-byte-short negative control.
    b = Block(r"(?<=ab)x", "lookaround")
    for s, p in [("zabx", 3), ("abx", 2), ("bx", 1), ("bx", 2)]:
        r = pcre2_search(r"(?<=ab)x", s, p)
        if r is None:
            b.ns(p, s)
        else:
            span, groups = r
            b.ms(p, s, span[0], span[1])
    rf.add(b, comment="ADVERSARIAL: tightest clamp boundary -- "
           "(?<=ab)x needs exactly 2 bytes before the position; "
           "\"bx\" from startpos=1 has only 1 byte available before "
           "startpos and MUST be NOMATCH (the byte at index 0 does not "
           "exist -- startpos=1 there is itself the very first position), "
           "while \"bx\" from startpos=2 (past the whole 2-byte subject) "
           "is also NOMATCH for the ordinary reason (no 'x' left).",
           pcre2_only=not py_ok(r"(?<=ab)x"))

    # -----------------------------------------------------------------
    # (7) sec 10.1 requirement 4a: an EMPTY CAPTURE inside a lookaround.
    # -----------------------------------------------------------------
    emit(rf, r"(?=(x*))a", "lookaround",
         ["a", "xa", "xxa", "b"],
         "sec 10.1 requirement 4a: empty capture inside a lookaround -- "
         "group 1 captures the EMPTY string (0,0) whenever no 'x' "
         "precedes 'a', a shape trail-discipline bugs specifically miss "
         "(an unset-vs-empty confusion).")

    # -----------------------------------------------------------------
    # (8) sec 10.1 requirement 4b: a RE-ENTERED GROUP across a
    # lookaround -- the group (and the lookaround's own inner capture)
    # get a fresh value on every iteration of the enclosing +, which is
    # exactly where S105's own trail-discipline lesson (backrefs/atomic
    # groups, "one construct over") applies here: sec 3.2(3)/3.3's undo
    # discipline must actually restore the PREVIOUS iteration's capture,
    # not merely stop writing new ones.
    # -----------------------------------------------------------------
    emit(rf, r"((?=(a+))a)+", "lookaround",
         ["aaab", "a", "aaaa", "b"],
         "sec 10.1 requirement 4b: re-entered group across a lookaround. "
         "Group 1 (the outer, re-entered each iteration of +) and group 2 "
         "(the lookahead's own inner capture, also re-entered) must both "
         "reflect the LAST successful iteration's values, not an earlier "
         "iteration's stale trail.")
    emit(rf, r"(?:(a)(?=(b))|(c)(?=(d)))+", "lookaround",
         ["abcd", "ab", "cdab", "abab", "x"],
         "sec 10.1 requirement 4b, second shape: a re-entered ALTERNATION "
         "whose two branches populate DIFFERENT capture groups through a "
         "lookaround each -- an iteration taking branch 2 must leave "
         "groups 1/2 exactly as branch 1's LAST iteration left them (PCRE2 "
         "capture semantics), not reset to unset.")

    header = (
        "# adversarial.rxt -- [M6.6.3] D27 hand-targeted adversarial corpus.\n"
        "# Six named trap classes from the brief's own \"Think:\" paragraph\n"
        "# (cut-on-wrong-arm, cursor-restore, forgot-to-cut, follow-scoping,\n"
        "# branch-width-boundary, lookbehind-vs-startpos-clamp) plus sec\n"
        "# 10.1's population requirement 4 (empty capture inside a\n"
        "# lookaround; a re-entered group across one). Every expectation is\n"
        "# still an oracle read -- only the pattern/subject CHOICE is\n"
        "# hand-designed here.\n"
    )
    rf.write(header)
    print("adversarial.rxt: %d blocks, %d cells, pcre2-only=%d python-verified=%d"
          % (rf.block_count(), rf.cell_count(), rf.pcre2only_count,
             rf.python_count))


if __name__ == "__main__":
    main()
