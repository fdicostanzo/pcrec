#!/usr/bin/env bash
# S1926 (lane sae2, 2026-11-09; span_arms E2, witness W-E3,
# docs/design/span_arms.md §4.5) -- A NEGATIVE LOOKAROUND'S BODY IS WALKED AS
# CONSUMED.
#
# T3 row E-4 of the necessary-run walk (src/facts/req.c `rb_zero_rows`) makes
# a negative lookaround CAT's width-0 unit: the run joins across it and its
# body, which the subject must NOT hold there, is never read. This plant walks
# the body as consumed text, so `xy(?<!ab)cd` claims `xyabcd` and the
# pre-check deletes `xycd`. Detector: the harness on
# tests/litscan/spanarms.rxt (both engines).
SAB_ID="S1926-negative-body-walked-consumed"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC="the necessary-run walk reads a negative lookaround's body as consumed text instead of the width-0 unit, so its run claims bytes the subject must not hold and the pre-check deletes matches"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sae2_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1926."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "xy(?<!ab)cd" && grep -qE "^#define RX_REQ_RUN \"78796364@[0-9]\"$" "$REACH_TMP/o.c" && echo REACH-WE3-RUN-JOINED'
SAB_REACH_EXPECT="REACH-WE3-RUN-JOINED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    case RB_ZERO_UNIT: rb_zero_unit_into(w, acc); return;'
SAB_AFTER='    case RB_ZERO_UNIT: if (a->k == A_LOOK && a->u.look.neg) { RbVal *v = pcrec_arena_alloc(&w->cx->arena, sizeof *v); rb_walk(w, a->l, v); rb_cat_into(w, acc, v); return; } rb_zero_unit_into(w, acc); return;   /* SABOTAGE S1926 */'
