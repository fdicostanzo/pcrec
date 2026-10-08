# S602 — [ART-POSS-ARMS]: ARM B RECOMPUTES A GROUP ALREADY IN PROGRESS
# (src/opt/possessify.c; docs/design/poss_arms.md rev 2.1 §8.2's plant row,
# lane possbuild).
#
# A DECLARED EQUIVALENT MUTANT, scored UNDETECTED (lane possfin; S219/S490's
# shape). It shipped as a termination row whose witness was a branching cycle,
# `(a\2\3)(b\1)(c\1)x+\1`, on the argument that without the guard the fold
# "explores 2^64 paths first". MEASURED, that is false twice over:
#  1. That witness never walks its cycle: each group's text begins with a
#     literal, so text_first stops before the reference.
#     A nullable-prefix cycle (`(a?\2\3)(b?\1)(c?\1)x+\1`) does walk it.
#  2. Even then the recomputation is not exponential. cap_group memoizes a
#     group the moment its first computation finishes, so the first descent
#     goes down one chain to PCREC_MAX_POSS_REF_DEPTH, unwinds, and every
#     sibling then hits CF_DONE. cap_group computations (instrumented, planted
#     vs clean): the nullable witness 65 vs 3, the non-nullable one 130 vs 6,
#     and k mutually-referencing nullable groups (k = 2..40) 64..202 vs 2..78,
#     i.e. 62..124 extra computations. The extra work is an ADDITIVE bound of
#     about 2 x depth, independent of branching.
# And the answers do not move: the planted compiler's artifacts are
# byte-identical to the clean compiler's on those witnesses and on 32 generated
# reference-cycle patterns (k = 2..40, dense and sparse), and its K35 census TSV
# (4,875 rows: marks, stamps, engines) is byte-identical to the clean one. Both
# sides widen the cycle's members to the same full set: the clean guard at the
# closing reference, the planted compiler at the depth bound.
# So the guard is a belt on a cost that the depth bound and the memo already
# cap; nothing observable (answer, artifact, compile time) separates the two
# compilers, and the cost has no counter in the tree (D77: no build ahead of
# a measured need). The suites below run and must read 0 fail; an answer
# divergence from this plant would read DETECTED (UNEXPECTED), which is the
# alarm. The guard is still correct and stays.
SAB_ID="S602-poss-b-in-progress-recomputed"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness possdiff"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='arm B recomputes a group whose value is in progress (a reference cycle); an equivalent mutant while the depth bound and the CF_DONE memo cap the recomputation at ~2 x depth'
SAB_DOC_FIGURE="DECLARED EQUIVALENT (the argument above). MEASURED 2026-10-07 (lane possfin, planted tree vs clean, aeae1964): artifacts byte-identical on the witness and 32 generated cycles, census TSV byte-identical (4,875 rows), cap_group computations 65 vs 3 (nullable witness). Scored UNDETECTED (EXPECTED): read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S602."
# [MECH-REACH] the site answers at HEAD: the stamp on a pattern whose verdict
# runs through the planted line.
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern '\''(a\2\3)(b\1)(c\1)x+\1'\'' && grep -q "^#define RX_VM_POSS_ARMS 0x4u$" "$REACH_TMP/o.c" && echo REACH-S602'
SAB_REACH_EXPECT="REACH-S602"
SAB_REACH_POP='tests/possessify/possessify.rxt|^pattern \(a\\2\\3\)\(b\\1\)\(c\\1\)x\+\\1$|1'
SAB_EXPECT=UNDETECTED
SAB_COUNT=1
SAB_BEFORE='    if (F->state[g] == CF_BUSY) return false;'
SAB_AFTER='    /* SABOTAGE S602: an in-progress group is recomputed */'
