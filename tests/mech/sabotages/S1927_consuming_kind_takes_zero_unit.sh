#!/usr/bin/env bash
# S1927 (lane sae2, 2026-11-09; span_arms E2, witness S-g at E2's site,
# docs/design/span_arms.md §4.5) -- A CONSUMING KIND IS SENT TO T3.
#
# The kind row's TEXT decides which nodes reach T3 (src/facts/req.c
# `rb_row_into`): ZERO does, ANY (a backreference, a variable, a consuming
# callout) is a gap. This plant sends ANY to T3 as well, so a backreference
# becomes the width-0 unit, `(ab)x\1y` claims `abxy` and the pre-check
# deletes `abxaby`. Detector: the harness on tests/litscan/spanarms.rxt (both
# engines).
SAB_ID="S1927-consuming-kind-takes-zero-unit"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC="the necessary-run walk sends a kind whose text is ANY (a backreference) to the zero-width rows, so it becomes the unit, a run is claimed across bytes it consumes and the pre-check deletes matches"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sae2_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1927."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(ab)x\\1y" && grep -qE "^#define RX_REQ_RUN \"616278@[0-9]\"$" "$REACH_TMP/o.c" && echo REACH-SG2-RUN-ABX'
SAB_REACH_EXPECT="REACH-SG2-RUN-ABX"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    case KTEXT_ANY:  rb_gap_into(acc, PCREC_W_UNBOUNDED); return;'
SAB_AFTER='    case KTEXT_ANY:  rb_zero_into(w, acc, a); return;   /* SABOTAGE S1927 */'
