# S603 — [ART-POSS-ARMS]: ARM A1 ADMITS A LAZY LOOP
# (src/opt/possessify.c; docs/design/poss_arms.md rev 2.1 §8.2's plant row,
# lane possbuild).
#
# N2 (§2.3): a lazy loop stops at its LOWEST exit where the continuation
# succeeds, and an empty bypass succeeds there; row 2's may_end catches that
# and A1 would skip it. Witness `(\w+?(?:\b|))` on "ab": 10.46 (0,1), the
# plant (0,2).
# Detectors (§8.1 item 5): the oracle-side .rxt cells in
# tests/possessify/possessify.rxt (harness) and the exhaustive possdiff
# (possdiff). REACH (§8.1 item 2) is SAB_REACH_POP: the witness is in the
# swept population.
SAB_ID="S603-poss-a1-admits-lazy"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness possdiff"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='arm A1 values gates for a lazy loop, skipping row 2'\''s may_end'
SAB_DOC_FIGURE="PREDICTED: harness on tests/possessify/possessify.rxt fails the witness block; possdiff diverges (or, for a termination/R-5 row, refuses) on it. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S603."
# [MECH-REACH] the site answers at HEAD: the stamp on a pattern whose verdict
# runs through the planted line.
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern '\''(\w+(?:\b|))'\'' && grep -q "^#define RX_VM_POSS_ARMS 0x2u$" "$REACH_TMP/o.c" && echo REACH-S603'
SAB_REACH_EXPECT="REACH-S603"
SAB_REACH_POP='tests/possessify/possessify.rxt|^pattern \(\\w\+\?\(\?:\\b\|\)\)$|1
tests/possessify/arms_reach.tsv|^\(\\w\+\?\(\?:\\b\|\)\)[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (P->fq.arm_a && base_ok && !lazy && a->u.rep.rmin >= 1 &&'
SAB_AFTER='    if (P->fq.arm_a && base_ok && a->u.rep.rmin >= 1 &&  /* SABOTAGE S603: greedy-only dropped */'
