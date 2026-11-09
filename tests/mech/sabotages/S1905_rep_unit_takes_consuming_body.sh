#!/usr/bin/env bash
# S1905 (lane sae1, 2026-11-09; span_arms E1, witness S-g spelled for E1's site,
# docs/design/span_arms.md §4.5) -- T2 ROW 1 TAKES A CONSUMING BODY.
#
# Row 1 of the necessary-run walk's repeat table (src/facts/req.c
# `rb_rep_rows`) makes a repeat of a WIDTH-0 body CAT's unit, so the run joins
# across it. This plant tests "the body carries no run" instead of "the body is
# width 0", which sends a consuming kind (a backreference, TEXT ANY) to the
# unit: `(ab)x\1*y` claims `abxy` and the pre-check deletes `abxaby`. Detector:
# the harness on tests/litscan/spanarms.rxt (both engines).
SAB_ID="S1905-rep-unit-takes-consuming-body"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC="the necessary-run walk's width-0 repeat row tests 'the body carries no run' instead of 'the body is width 0', so a consuming body (a backreference) becomes the unit, a run is claimed across it and the pre-check deletes its matches"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sae1_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1905."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(ab)x\\1*y" && grep -qE "^#define RX_REQ_RUN \"616278@[0-9]\"$" "$REACH_TMP/o.c" && echo REACH-SG-RUN-ABX'
SAB_REACH_EXPECT="REACH-SG-RUN-ABX"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return b->runs.maxw == 0;'
SAB_AFTER='    return b->runs.best.n == 0;   /* SABOTAGE S1905 */'
