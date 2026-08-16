#!/usr/bin/env python3
"""make_corpus.py — the PRODUCER of tests/rungselect/rungselect.rxt.

Committed for R24 M-F4's reason: a corpus whose expectations were hand-written,
or produced by a script nobody kept, cannot be re-derived when the oracles move.
Every expectation in that file came from HERE, from BOTH oracles (python3 `re`,
and libpcre2 through ctypes), and a cell the two disagreed on is REPORTED
rather than resolved.

THE ORACLE PLUMBING IS IMPORTED, NOT COPIED, from the possessification lane's
`../possessify_impl/gen_rxt.py`. That file already carries the instrument note
this generator would otherwise have had to rediscover — `pcre2_match` returns
the number of ovector pairs it FILLED, which is (highest participating group
+ 1) and not the pattern's group count, so reading only `rc` pairs makes every
trailing UNSET group vanish rather than read as unset. It produced seven
phantom "oracle disagreements" on that lane's first run; it would have produced
more here, because this rung's whole capture story is about groups that some
iterations do not enter.

EVERY PATTERN IS CAPTURE-BEARING, and that is not decoration. Under the DEFAULT
engine choice a capture-free pattern routes to the DFA and never reaches
src/gen/emit_vm.c at all, so a rung in that file would be structurally invisible
to it — the exact defect the possessify lane measured on its own first version
(33 of 38 patterns DFA-routed). `.rxt` blocks carry no engine flag, so the
pattern text has to force the VM itself, and a capturing group is what does it.

Usage: python3 docs/design/rungselect_impl/make_corpus.py tests/rungselect/rungselect.rxt
"""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "possessify_impl"))
from gen_rxt import emit   # noqa: E402

# Subjects. The families that discriminate for THIS rung: runs of the body's
# own alphabet at every length across the loop's boundary counts, the same runs
# with and without the follow, and mixed runs — because the capture rule's whole
# subtlety is WHICH iteration last entered a group, which only a mixed run can
# ask about.
S = ["", "a", "b", "c", "d",
     "ac", "bc", "abc", "bac", "aac", "bbc", "abbc", "babc", "aabbc",
     "ababc", "bababc", "aaaac", "bbbbc", "aaaaac", "bbbbbc",
     "abababc", "aabbaabbc",
     "aa", "ab", "ba", "bb", "aaa", "aab", "aba", "abb", "baa", "bab",
     "aaaa", "abab", "bbaa", "aaaaa", "ababab",
     "za", "zab", "zabc", "zaabbc", "q", "aq", "cq", "abcq"]

# Subjects for the multi-byte-branch families, whose alphabet is different.
T = ["", "w", "x", "y", "z", "xy", "xyw", "zw", "xyzw", "zxyw", "zzzw",
     "xyxyw", "zxyzw", "xyzxyw", "xyxyxyw", "zzw", "wq", "xyq",
     "p", "pq", "r", "pqd", "rd", "pqrd", "rpqd", "pqpqd", "rrd", "d",
     "pqrpqd", "cpqd", "crd", "cd"]

BLOCKS = [
 # ---- the motivating cell's own family -------------------------------------
 (["THE MOTIVATING CELL, at a count small enough that the GROUND TRUTH still",
   "exists: `((a)|b){0,4000}c` is what this rung is for, and replication is",
   "refused above PCREC_MAX_VM_REPEAT_COPIES, so the answers are pinned here",
   "at a count both emissions can produce.",
   "",
   "Group 2 is the whole point. It is inside ONE BRANCH, so an iteration that",
   "takes `b` does not enter it -- and PCRE2 keeps the value from the last",
   "iteration that DID. That is the clause the plan row's constant-offset",
   "derivation got wrong on 1,799 of 15,036 matches (eng_brep_design.md",
   "§3.4), and the cells below are where a regression to it would show:",
   "\"abbc\" must give group 2 = the leading `a`, not unset."],
  "((a)|b){0,4}c", S),

 (["The same loop with an OVERLAPPING follow. FIRST(body) = {a,b} and the",
   "follow is `a`, so the quantifier is NOT possessifiable and the emitted",
   "loop owes a real RETREAT -- the backward walk's hard half, and the only",
   "family in this file that exercises it."],
  "((a)|b){0,4}a", S),

 (["LAZY, which emits a genuinely different shape: it commits at the MINIMUM",
   "and extends forward, where the greedy form commits at the maximum and",
   "retreats. R24 S-F1's rule that an all-greedy sweep is structurally blind",
   "applies to the emitted shape as much as to the analysis."],
  "((a)|b){0,4}?a", S),
 (["LAZY with a disjoint follow, where the loop is possessified and both",
   "preferences are forced to the same maximal exit (§2.2's own conclusion)."],
  "((a)|b){1,3}?c", S),

 (["m > 0: the mandatory iterations are counted by the same scan, and the",
   "low-water slot is written at the m-th boundary rather than at entry."],
  "((a)|b){2,4}c", S),
 (["m == n: one exit, so no retreat frame is owed at all -- a distinct",
   "emitted shape, not a special case of the bounded one."],
  "((a)|b){3}c", S),

 (["UNBOUNDED, which takes the same code path with no ceiling. Worth pinning",
   "separately because the frames rung treats bounded and unbounded as two",
   "rungs and this one does not."],
  "((a)|b)*c", S),
 (["UNBOUNDED with m > 0 and an overlapping follow."],
  "((a)|b)+a", S),

 # ---- multi-byte branches --------------------------------------------------
 (["BRANCHES OF DIFFERENT LENGTH, which is where a backward walk has to",
   "DECIDE the iteration's length from the byte it lands on rather than",
   "subtract a constant stride. `(ab){0,4}` would take the cursor rung one",
   "step up the ladder; this cannot."],
  "((x)y|z){0,4}w", T),
 (["Two groups in one body, only ONE of which any given iteration enters --",
   "so the two are witnessed at different iterations by the same walk, which",
   "is the general form of the `((a)|b)` case above."],
  "(?:(p)q|(r)){0,4}d", T),
 (["The same, with something in front of it, so the search entry has to",
   "advance the start position before the loop ever runs."],
  "c(?:(p)q|(r)){0,4}d", T),

 # ---- the declines, pinned as answers rather than as verdicts --------------
 (["DECLINE: reverse-ambiguous. Forward-deterministic, but a backward walk",
   "from a boundary of \"abab\" can stop at 3 (branch `b`) or at 2 (branch",
   "`ab`), both genuine body matches. It stays on the FRAMES rung, and its",
   "answers are pinned here so that a future widening of the analysis that",
   "took it would have to keep them."],
  "(x)(?:ab|b){0,4}c", S),
 (["DECLINE: forward-ambiguous (U1) -- `(a|ab)` is the body whose iteration",
   "can end in two places, the 117-counterexample family of §2.4."],
  "(x)(a|ab){0,4}c", S),
 (["DECLINE: not prefix-free (U2). No alternation is needed for this one:",
   "`(?:ab?)`'s accepting position `a` simply has an outgoing edge."],
  "(x)(?:ab?){0,4}b", S),
 (["DECLINE: a nullable body has no strictly-increasing exit chain, and the",
   "empty-iteration territory §6 is about."],
  "(x)(?:a|){0,4}c", S),
 (["DECLINE (single-level scope bound): the INNER quantifier qualifies on its",
   "own shape and is declined because it sits inside another quantifier's",
   "body. The answers are pinned so that lifting the bound later has to keep",
   "them."],
  "(x)(?:((a)|b){0,2}c){0,3}d", S),

 # ---- mixed artifacts ------------------------------------------------------
 (["A THREE-RUNG artifact: `a*` on the cursor, `((a)|b){0,3}` on this rung,",
   "and `(?:ab|b){0,3}` reverse-ambiguous on the frames. One pattern whose",
   "answers depend on all three emissions agreeing."],
  "a*((a)|b){0,3}c(?:ab|b){0,3}d", S),
 (["TWO rung loops in one pattern, so the per-loop slot triples and the",
   "SHARED capture-recovery locals are exercised at once."],
  "((a)|b){0,3}c(?:(p)q|(r)){0,3}d", S + T),
 (["The rung INSIDE a group, so the group's own span has to survive every",
   "retreat the inner loop performs."],
  "(((a)|b){0,4})c", S),

 # ---- the only nested quantifier the rung admits ---------------------------
 (["A NESTED FIXED-COUNT quantifier, which is the ONLY nested quantifier the",
   "rung admits and the only shape that exercises the backward emitter's own",
   "replication arm. It has to sit in the MIDDLE of the body, and that is",
   "measured rather than stylistic: the Glushkov construction models `{2}` as",
   "a LOOP (it links last to first whenever rmax > 1), so a fixed repeat at",
   "either END of a body gives that end's positions a back edge and",
   "prefix-freeness fails in that direction. Hence the `x` and the `y`."],
  "(?:x((a)|b){2}y){0,3}z",
  ["", "z", "xaby", "xabyz", "xaayz", "xbbyz", "xbayz",
   "xabyxbayz", "xabyxaayz", "xaayxbbyz", "xabyxabyxaayz", "xayz", "xaaayz",
   "xy", "xz", "abyz", "q", "xabyq"]),
 (["The same shape lazy, and the same shape without the inner group."],
  "(?:x((a)|b){2}y){0,3}?z",
  ["", "z", "xabyz", "xaayz", "xbbyz", "xabyxbayz", "xabyxaayz", "xayz"]),

 (["A group in EVERY branch, so one walk publishes two groups per step and",
   "each keeps the value from the last iteration that entered ITS branch."],
  "(?:(x)(?:y|z)){0,3}w", T),
]

HEADER = """\
# tests/rungselect/rungselect.rxt — the [ENG-BREP] REVERSE-DETERMINISTIC rung's
# oracle-verified corpus (docs/design/engine_m4.md §2.5,
# docs/design/eng_brep_design.md §3).
#
# GENERATED, do not hand-edit. Producer:
# docs/design/rungselect_impl/make_corpus.py (committed, re-runnable).
#
# EVERY EXPECTATION HERE WAS PRODUCED BY BOTH ORACLES AND AGREED. Each
# (pattern, subject) cell's span and every capture slot were taken from python3
# `re` AND from libpcre2, and a cell the two disagreed on was reported rather
# than resolved.
#
# WHAT THIS FILE IS FOR, and what it is NOT for. It pins the ANSWERS around the
# rung -- what each pattern matches, whether or not the rung fires on it. It
# cannot see the rung itself: a quantifier emitted as one body copy plus a
# backward walk and the same quantifier replicated `n` times match identically,
# which IS the claim. The check that can see the rung is the pcrec-vs-pcrec
# differential (run_rungdiff.sh); the check that says WHICH quantifier took
# which rung is the artifact's own <PREFIX>_VM_RUNGS stamp
# (run_rungselect_tests.sh). All three are needed and none substitutes for
# another.
#
# EVERY PATTERN IS CAPTURE-BEARING on purpose. A capture-free pattern routes to
# the DFA under the default engine choice and never reaches src/gen/emit_vm.c,
# so a rung would be structurally invisible to it -- the defect the
# possessification lane measured on its own first corpus (33 of 38 patterns
# DFA-routed, 3 carrying the feature under test).
"""


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "-"
    f = sys.stdout if out == "-" else open(out, "w")
    f.write(HEADER)
    n = emit(BLOCKS, f)
    if f is not sys.stdout:
        f.close()
    print("oracle disagreements:", n, file=sys.stderr)
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
