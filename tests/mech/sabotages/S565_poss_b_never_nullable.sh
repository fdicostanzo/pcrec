# S565 — [ART-POSS-ARMS]: ARM B CALLS EVERY REFERENCE NON-NULLABLE
# (src/opt/possessify.c; docs/design/poss_arms.md rev 2.1 §8.2's plant row,
# lane possbuild).
#
# A group that can capture "" makes its reference consume nothing, so the
# follow runs on past it (§3.2). Witness `(a?)x+\1x` on "xx": 10.46 (0,2),
# the plant NOMATCH.
# Detectors (§8.1 item 5): the oracle-side .rxt cells in
# tests/possessify/possessify.rxt (harness) and the exhaustive possdiff
# (possdiff). REACH (§8.1 item 2) is SAB_REACH_POP: the witness is in the
# swept population.
SAB_ID="S565-poss-b-never-nullable"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness possdiff"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='arm B forces nullable(\\n) false'
SAB_DOC_FIGURE="PREDICTED: harness on tests/possessify/possessify.rxt fails the witness block; possdiff diverges (or, for a termination/R-5 row, refuses) on it. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S565."
# [MECH-REACH] the site answers at HEAD: the stamp on a pattern whose verdict
# runs through the planted line.
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern '\''(a)x+\1'\'' && grep -q "^#define RX_VM_POSS_ARMS 0x4u$" "$REACH_TMP/o.c" && echo REACH-S565'
SAB_REACH_EXPECT="REACH-S565"
SAB_REACH_POP='tests/possessify/possessify.rxt|^pattern \(a\?\)x\+\\1x$|1
tests/possessify/arms_reach.tsv|^\(a\?\)x\+\\1x[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (f->a->u.bref.caseless) bref_fold(q->cx, f->a->u.bref.ucp, f->acc.f);
    q->b_used = true;'
SAB_AFTER='    if (f->a->u.bref.caseless) bref_fold(q->cx, f->a->u.bref.ucp, f->acc.f);
    f->acc.nullable = false;  /* SABOTAGE S565: never nullable */
    q->b_used = true;'
# RE-ANCHORED (lane k147fix, 2026-11-20, K147/K149): arm B's result is first_eval's `refs:` block, the reference read off its frame; same site, same plant.
