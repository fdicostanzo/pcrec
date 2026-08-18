#!/usr/bin/env python3
"""[M6.1]/R30 E1 — assertion context at `startpos > 0` comes from a byte
OUTSIDE the search window.

The design's first draft claimed every construct in this module is one of three
mechanisms. R30 refuted that: `\\b`, `\\B` and `(?m)^` at `startpos > 0` depend
on `s[startpos-1]`, a byte the search window does not contain, and a trailing
`\\b` depends on `s[end]`, a byte the REVERSE walk never consumes. Neither DFA
engine has a mechanism for either today — both start states are emitted as
compile-time constants (`src/gen/emit_dfa.c:946` forward, `:1029` reverse).

THE DISTINGUISHING PROPERTY, and why a slice is not a substitute: searching
`s` from `startpos` is NOT the same as searching `s[startpos:]` from 0. This
probe measures both against libpcre2 so the difference is a table rather than
an argument. A row where `whole@startpos` and `slice@0` DISAGREE is a cell an
implementation that slices (or that seeds context as "start of subject") gets
wrong.

These cells are the design's Wave B landing conditions. They are also run
through the find-all loop of docs/spec/match_api.md S3.1, because that loop
calls the search entry with a moving `startpos` and is where the defect would
reach an ordinary consumer.

Usage: probe_startpos_context.py
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P2 = os.path.join(HERE, os.pardir, os.pardir,
                  "eng_brep_measurements", "probes", "pcre2_ctypes.py")
spec = importlib.util.spec_from_file_location("pcre2_ctypes", P2)
p2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p2)

# (pattern, subject, startpos, what the cell is for)
CELLS = [
    (r"\bfoo",   "xfoo",      1, "prev byte is a word char, so \\b FAILS at 1 "
                                 "-- a slice-blind engine MATCHES here"),
    (r"\bfoo",   " foo",      1, "the satisfiable twin: prev byte is a space, "
                                 "\\b HOLDS -- both agree, so the pair "
                                 "discriminates rather than just refusing"),
    (r"\Bfoo",   "xfoo",      1, "the \\B mirror: HOLDS where \\b fails, so a "
                                 "slice-blind engine gives NO MATCH where "
                                 "PCRE2 matches (the opposite direction)"),
    (r"\Bfoo",   " foo",      1, "the \\B twin: fails where \\b holds"),
    (r"foo\b",   "foox",      0, "TRAILING \\b depends on s[end] -- the byte "
                                 "the REVERSE walk never consumes. Whole/slice "
                                 "agree (startpos 0); the hazard is the "
                                 "reverse machine, not the slice"),
    (r"foo\b",   "foo ",      0, "trailing \\b, satisfiable twin"),
    (r"(?m)^b",  "ab\nb",     1, "(?m)^ MID-LINE: at startpos 1 the prev byte "
                                 "is 'a', so ^ fails at 1 and the match is the "
                                 "next line -- a slice-blind engine treats "
                                 "position 1 as a line start and matches there"),
    (r"(?m)^b",  "ab\nb",     3, "(?m)^ at a real line start: prev byte is "
                                 "'\\n', so both agree"),
    (r"\bfoo",   "xfoo foo",  1, "the sharpest cell: a slice-blind engine does "
                                 "not merely over-match, it reports the WRONG "
                                 "OCCURRENCE -- (1,4) instead of (5,8)"),
    (r"\Afoo",   "xfoo",      1, "NOT a pcrec defect, and included to bound the "
                                 "claim: \\A differs under SLICING too, but "
                                 "pcrec never slices -- it passes startpos, and "
                                 "\\A/`^` route to ENG_ATTEMPT whose start "
                                 "state is already chosen at runtime by "
                                 "`start == 0`. The mechanism E1 asks for is "
                                 "needed for the CONTEXT assertions above, not "
                                 "for this one"),
]

# The find-all dimension: docs/spec/match_api.md S3.1's loop calls the search
# entry with a MOVING startpos, so every iteration after the first re-poses the
# question these cells ask. Reported as the match sequence.
# Chosen so the RESUME position lands mid-word: that is the only place the
# loop can ask the E1 question, and a set of cases that all resume at a word
# boundary would report "same" while proving nothing (the first draft of this
# probe did exactly that).
FINDALL = [
    (r"\Bfoo", "xfoofoo",    "resume lands mid-word: \\B holds there in the "
                             "whole subject and FAILS at the slice's start"),
    (r"\Boo",  "foofoofoo",  "the same shape, three occurrences deep"),
    (r"\bfoo", "foo xfoo foo", "CONTROL: every resume lands at a boundary, so "
                               "both agree -- a suite of only these would "
                               "prove nothing"),
]


def search(pat, subj, start):
    got = p2.compile(pat.encode()).search(subj.encode(), start)
    return got[0] if got else None


def main():
    print("libpcre2 %s ; python %s" % (p2.version(), sys.version.split()[0]))
    print()
    print("%-9s %-11s %-4s %-11s %-11s %s" %
          ("pattern", "subject", "spos", "whole@spos", "slice@0", "verdict"))
    differ = 0
    for pat, subj, start, why in CELLS:
        whole = search(pat, subj, start)
        sl = search(pat, subj[start:], 0)
        # Re-base the slice answer into whole-subject coordinates so the two
        # are comparable at all.
        sl_rebased = None if sl is None else (sl[0] + start, sl[1] + start)
        same = whole == sl_rebased
        differ += not same
        print("%-9s %-11r %-4d %-11s %-11s %s" %
              (pat, subj, start, whole, sl_rebased,
               "same" if same else "*** DIFFER ***"))
        print("%-9s %s" % ("", "  " + why))
    print()
    print("%d of %d cells DIFFER between searching the whole subject from "
          "startpos and searching the slice from 0." % (differ, len(CELLS)))
    print("Each differing cell is one an implementation that seeds assertion")
    print("context as `start of subject` -- which is what a compile-time")
    print("constant start state does -- gets WRONG.")

    print()
    print("=== the same question through the S3.1 FIND-ALL loop ===")
    print("The loop passes its resume position as `startpos`, so every")
    print("iteration after the first asks exactly the question above. Each")
    print("row shows the true sequence, then what a slice-blind engine")
    print("(context re-seeded as start-of-subject each iteration) reports.")
    print()
    for pat, subj, why in FINDALL:
        true_spans, blind_spans = [], []
        for spans, blind in ((true_spans, False), (blind_spans, True)):
            p = 0
            while p <= len(subj):
                got = (search(pat, subj[p:], 0) if blind
                       else search(pat, subj, p))
                if got is None:
                    break
                a, b = (got[0] + p, got[1] + p) if blind else got
                spans.append((a, b))
                p = b if b > a else a + 1
                if len(spans) > 12:
                    break
        flag = "" if true_spans == blind_spans else "   *** DIFFER ***"
        print("  %-8s %-14r  %s" % (pat, subj, why))
        print("      true        %s" % (true_spans,))
        print("      slice-blind %s%s" % (blind_spans, flag))


main()
