# S165 ([DD-14], design SS8.2, SS9.3 S-SR17 -- LANDED IN WAVE B+C RATHER THAN
# WAVE E) -- THE PREFILTER IS OFF FOR A CALL-BEARING PATTERN.
#
# ERASING A CALL IS NOT A SUPERSET, IT IS A DIFFERENT LANGUAGE, and the
# counterexample is one line (SS8.2): `a(?1)b` with group 1 = `x` matches
# "axb"; erase the call and `ab` is left, which does not. So a prefilter built
# from the erasure would REJECT a matching subject -- a false negative, which
# is the one thing a prefilter may never be. That is unlike `lookaround`'s
# erasure (a one-line superset proof) and exactly like `backrefs`'.
#
# WHY IT IS IN THIS WAVE AND NOT WAVE E, which the row records because the
# design's own schedule says otherwise. `src/ir/nfa.c`'s `compile_ast` has an
# `A_CALL` arm that `ctx_fail`s by name -- design SS4.4a site (25), DECLINE,
# annotated "unreachable: VM_ONLY, no prefilter" -- and "unreachable" was true
# only while nothing PRODUCED an `A_CALL`. MEASURED on this branch before the
# predicate existed: `(a)(?1)`, `(?R)` and `(?<n>a)(?&n)` each answered
# `pcrec: internal error: bad AST node`, because a capture-bearing pattern
# routes to the VM, the VM asks for its prefilter, and the prefilter build
# walks a node it refuses. The choice was not "ship the optimisation early", it
# was "ship a compiler that cannot compile the module's own corpus".
#
# SO THE PREDICTION IS DIFFERENT ON THIS TREE FROM SS9.3's, and both are
# detections. SS9.3 predicts a SILENT SKIP -- "a matching subject is skipped",
# which is what a built-and-wrong prefilter does. Here the build REFUSES first,
# so the observable is a compile error naming the internal wall. The silent-skip
# form becomes reachable at WAVE G, which builds SS8.3's sound approximation
# (splice an acyclic callee's NFA fragment, `Sigma*` for a cyclic one) and makes
# an erased machine constructible at all -- and this row's prediction should be
# RE-READ then rather than assumed unchanged.
#
# THE COST OF THE PREDICATE IS MEASURED AND STATED rather than hidden: 21x-350x
# on the sparse-candidate shape a prefilter exists for, over the NON-RECURSIVE
# half of the population (SS8.3, on the inlined equivalents, 15 pairs verified
# equivalent at 420 cells / 0 disagreements before any timing).
SAB_ID="S165-prefilter-on-call"
SAB_FILE="src/opt/select_engine.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="fit.prefilter is left ON for a call-bearing pattern, so the hybrid is built from a call-ERASED DFA -- which is not a superset but a DIFFERENT language, so a matching subject is skipped"
SAB_DOC_FIGURE="LANDED EARLY AND THE ROW SAYS SO. Design 11 puts this predicate in wave E; it landed in wave B+C because without it src/ir/nfa.c's A_CALL arm is REACHABLE and every capture-bearing call pattern answered 'internal error: bad AST node' -- MEASURED on this branch before the line existed. So the sabotage's own prediction changes with it: on THIS tree the failure is a COMPILE ERROR (nfa.c refuses the node) rather than 8.2's silent skip, because wave G's 8.3 approximation -- the arm that would make the erasure buildable -- does not exist yet. Both are detections; only the second is the one 9.3 predicted."
SAB_COUNT=1
# [SEL-1] RE-ANCHORED 2026-08-28 (manager's landing-battery finding): the
# guard gained a THIRD disjunct, `cx->dfa_disabled` (auto's DFA-cap-overflow
# fallback drops the prefilter the same silent way has_bref/has_call already
# do), so the two-disjunct line this row anchored on stopped existing — the
# same re-home shape S102's own note records one disjunct earlier. Still
# targets `has_call` ALONE: `has_bref` and `cx->dfa_disabled` are carried
# through UNCHANGED in `SAB_AFTER`, so this row's population stays exactly
# "a call-bearing pattern's prefilter turns on", not wider.
# [OPT-4] 2026-08-29: ANCHOR RE-DERIVED FROM THE LIVE SOURCE. The [SEL-1]
# rung split this expression over three lines — `cx->dfa_disabled` alone became
# `(cx->dfa_disabled && !cx->prefilter_collapse_retry)`, because the fallback
# now tries a count-collapsed prefilter before dropping the prefilter outright.
# The sabotage is UNCHANGED in meaning: it still disables exactly one conjunct
# and carries the rest through verbatim.
SAB_BEFORE='        fit.prefilter = (has_bref || has_call ||
                         (cx->dfa_disabled && !cx->prefilter_collapse_retry))
                        ? false'
SAB_AFTER='        fit.prefilter = (has_bref || false ||   /* SABOTAGE S165 */
                         (cx->dfa_disabled && !cx->prefilter_collapse_retry))
                        ? false'
