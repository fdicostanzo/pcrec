# S262 — [TOUR-4/K61] `clo_open`'s DFA_INVARIANT CONDITION IS INVERTED, SO
# THE "loop not already open" CHECK FIRES ON EVERY LOOP A DFA BUILD OPENS
# (src/ir/dfa.c) — the regression guard for K61 (docs/dev/known_issues.md),
# which turned `DFA_INVARIANT` from an unconditional `abort()` into a
# `pcrec_ctx_fail` refusal so a "cannot happen" DFA closure premise no longer
# kills the caller's process (docs/spec/match_api.md §8.1's caller-survives
# promise; r61 finding F1).
#
# `lctx_find(cl->ctxs, ctx, s) < 0` (true exactly when `s` is NOT already
# open on this path -- the ordinary, expected case) becomes `>= 0` (true
# only in the "cannot happen" case), which is the same inversion shape as
# every other DFA_INVARIANT sabotage in this family: the CONDITION the
# macro tests is flipped, not the macro's own response to it. Since
# `lctx_find` returns -1 on essentially every real closure (a fresh loop
# is not yet on the open-loop stack), the invariant now fires on the FIRST
# loop any DFA build opens -- which is any pattern containing a repeated
# non-trivial subpattern (`a+`, `\d*`, `(?:ab){2,5}`, ...), a huge and
# ordinary fraction of the corpus.
#
# WHAT THIS PROVES ABOUT THE FIX, NOT JUST ABOUT THE INVARIANT: before K61,
# this same plant made `abort()` fire on the first such pattern the harness
# compiled, killing the whole test process with no diagnostic and no further
# rows scored -- the exact caller-killing failure mode `docs/spec/
# match_api.md`'s promise exists to rule out. After K61, the identical
# plant makes every reached pattern refuse cleanly (`pcrec_compile` returns
# -1 with "internal error: DFA closure tried to open an already-open loop
# ..."), so the harness runs to completion and reports an ordinary,
# non-crashing sea of compile failures -- detected the same way any other
# refusal is, never a crash.
SAB_ID="S262-dfa-invariant-loop-open-inverted"
SAB_FILE="src/ir/dfa.c"
SAB_SUITES="harness"
SAB_DESC="clo_open's DFA_INVARIANT condition is inverted (lctx_find(...) < 0 becomes >= 0), so the 'loop not already open' check fires on the first loop any DFA build opens instead of only on a genuine open-loop-context conflict -- K61's regression guard: post-fix this refuses cleanly (pcrec_ctx_fail, an ordinary -1-with-diagnostic) on every reached pattern rather than abort()ing the caller's process the way the pre-K61 macro would have"
SAB_DOC_FIGURE="tests/harness/run.sh over the full .rxt corpus is the detector: essentially every pattern with a repeated non-trivial subpattern refuses to compile under this plant, so 'cases failed' moves from 0 to a large count and the run completes cleanly (no crash, no early termination) -- the harness's own survival through the whole corpus is itself part of what this row certifies, not only the failure count. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S262."
SAB_COUNT=1
SAB_BEFORE='    DFA_INVARIANT(cl->cx, lctx_find(cl->ctxs, ctx, s) < 0,
                  "DFA closure tried to open an already-open loop "
                  "(open-loop-context no-repeats premise violated)");'
SAB_AFTER='    DFA_INVARIANT(cl->cx, lctx_find(cl->ctxs, ctx, s) >= 0,   /* SABOTAGE S262: fires on every loop-open instead of only a real conflict */
                  "DFA closure tried to open an already-open loop "
                  "(open-loop-context no-repeats premise violated)");'
