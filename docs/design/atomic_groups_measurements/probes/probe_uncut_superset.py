"""probe_uncut_superset.py — MEASURED, libpcre2 only, SWEEP.

[M6.4.1] §4 (the hybrid hazard). The DFA prefilter runs the pattern with its
atomicity ERASED — it has no other choice: subset construction keeps every
alternative alive, which IS the non-atomic semantics (Frank's 2026-08-12
companion note). So the prefilter answers for the UNCUT language. This probe
measures, over a generated family rather than over three hand-picked cells,
exactly which of the prefilter's three outputs survive that erasure:

  (R1) REJECTION is SOUND        — uncut nomatch  =>  cut nomatch
  (R2) START is a LOWER BOUND    — start_uncut <= start_cut, whenever the cut
                                    pattern matches at all
  (R3) END is NOT a BOUND in either direction — and this is the finding: it
       is the `window_end` the emitted search loop passes to
       `<prefix>_match_anchored` as the [M4.6d] MRL CEILING
       (src/gen/emit_vm.c:5225-5236), where a ceiling that is too SMALL
       DELETES a real match.

METHOD. Generate patterns of the shape PRE (?>ALT) MID | TAIL over a small
grammar, and for each one build its UNCUT twin by deleting the `?>` (which
turns `(?>X)` into a plain non-capturing group `(X)` -- so the twin is the
same automaton the NFA builder would produce with atomicity dropped, which is
precisely what the prefilter is). Run BOTH through libpcre2 on every subject.

WHY THE TWIN IS BUILT BY TEXT SUBSTITUTION AND NOT BY A SECOND HAND-WRITTEN
PATTERN: a hand-written twin can silently differ in something other than the
atomicity, which would make every reported divergence unattributable. `(?>` ->
`(?:` is a two-byte edit that provably touches nothing else.

EXCLUDED, and it matters: the twin substitution is NOT applied to possessive
SUFFIXES here. `X*+` -> `X*` is the same erasure, but the suffix spelling can
also change what the PRECEDING item may do (U9), so mixing the two spellings
in one sweep would make U9's PCRE2-side quirk look like a prefilter finding.
The suffix family gets its own section in probe_atomic_semantics.py.
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "eng_brep_measurements", "probes"))
import pcre2_ctypes as P  # noqa: E402

PRE  = ["", "a", "a*", "x*", "(?:a|b)"]
ALTS = ["a|ab", "ab|a", "a|ab|abc", "a*|ab", "a|b", "ab|abc", "a+|ab"]
MID  = ["", "b", "c", "bc", "b*c", "a"]
TAIL = ["", "abcd", "aab", "ab", "abbc", "xabc"]
SUBJ = ["", "a", "ab", "abc", "abcd", "aab", "aabc", "abbc", "xabc", "xxabcd",
        "aaab", "bca", "abcabc", "ba"]


def run(rx, subj, start=0):
    try:
        r = rx.search(subj, start)
    except P.Pcre2Error:
        return None
    return r[0] if r else None


def main():
    print("libpcre2:", P.version())
    print()
    pats = []
    for pre, alt, mid, tail in itertools.product(PRE, ALTS, MID, TAIL):
        cut = "%s(?>%s)%s" % (pre, alt, mid)
        if tail:
            cut += "|" + tail
        unc = cut.replace("(?>", "(?:")
        pats.append((cut, unc))
    # de-duplicate: different (pre,alt,mid,tail) can spell the same pattern
    seen = set()
    uniq = []
    for c, u in pats:
        if c in seen:
            continue
        seen.add(c)
        uniq.append((c, u))

    n_cells = 0
    n_both_match = 0
    r1_viol = []      # uncut says nomatch, cut says match  -> rejection UNSOUND
    r2_viol = []      # start_uncut > start_cut             -> not a lower bound
    r3_short = []     # end_uncut < end_cut                 -> CEILING UNSOUND
    r3_long = []      # end_uncut > end_cut                 -> ceiling merely loose
    start_moved = []  # start_uncut < start_cut             -> the retry loop is LIVE
    for cut, unc in uniq:
        try:
            rc = P.compile(cut)
            ru = P.compile(unc)
        except P.Pcre2Error:
            continue
        for s in SUBJ:
            n_cells += 1
            mc = run(rc, s)
            mu = run(ru, s)
            if mc is None:
                continue
            if mu is None:
                r1_viol.append((cut, unc, s, mc, mu))
                continue
            n_both_match += 1
            if mu[0] > mc[0]:
                r2_viol.append((cut, unc, s, mc, mu))
            elif mu[0] < mc[0]:
                start_moved.append((cut, unc, s, mc, mu))
            if mu[1] < mc[1]:
                r3_short.append((cut, unc, s, mc, mu))
            elif mu[1] > mc[1]:
                r3_long.append((cut, unc, s, mc, mu))

    print("patterns (unique): %d   cells (pattern x subject): %d   "
          "cells where the CUT pattern matches and so does its twin: %d"
          % (len(uniq), n_cells, n_both_match))
    print()

    def report(name, rule, lst, verdict_zero, verdict_nonzero, show=6):
        print("%s" % name)
        print("  rule under test : %s" % rule)
        print("  violations      : %d" % len(lst))
        print("  verdict         : %s"
              % (verdict_zero if not lst else verdict_nonzero))
        for cut, unc, s, mc, mu in lst[:show]:
            print("     cut %-28s uncut %-28s subj %-9s cut=%s uncut=%s"
                  % (cut, unc, repr(s), mc, mu))
        if len(lst) > show:
            print("     ... %d more" % (len(lst) - show))
        print()

    report("R1  SOUND REJECTION",
           "uncut nomatch => cut nomatch (the prefilter may still reject)",
           r1_viol,
           "HOLDS on this family -- the prefilter's `return 0` stays sound",
           "REFUTED -- the prefilter may NOT reject")
    report("R2  START IS A LOWER BOUND",
           "start_uncut <= start_cut (the prefilter's start may seed the "
           "first attempt, never be reported)",
           r2_viol,
           "HOLDS on this family",
           "REFUTED -- the prefilter's start may not even seed the attempt")
    report("R3a END IS AN UPPER BOUND (the MRL-CEILING rule)",
           "end_uncut >= end_cut  -- REQUIRED for `window_end` to be a sound "
           "MRL ceiling",
           r3_short,
           "holds on this family (which would NOT license the rule -- see the "
           "note below)",
           "REFUTED -- `window_end` from the prefilter DELETES real matches")
    report("R3b end_uncut > end_cut (ceiling merely loose, harmless)",
           "informational: how often the uncut end OVERSHOOTS",
           r3_long, "never overshoots", "overshoots (harmless direction)")
    print("INFORMATIONAL: cells where start_uncut < start_cut (the emitted "
          "search loop's `attempt_position++` retry is REACHED): %d"
          % len(start_moved))
    for cut, unc, s, mc, mu in start_moved[:6]:
        print("     cut %-28s subj %-9s cut=%s uncut=%s" % (cut, repr(s), mc, mu))
    print()
    print("NOTE ON R3a's ZERO CASE: a zero here would be a property of THIS "
          "family, not a theorem. The design does not rest on it either way -- "
          "see atomic_groups_design.md §4.3.")


main()
