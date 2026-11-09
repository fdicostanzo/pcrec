#!/usr/bin/env bash
# S1925 (lane sae2, 2026-11-09; span_arms E2, witness S-L,
# docs/design/span_arms.md §4.1 S16 and §5.7) -- A POSITIVE LOOKAROUND'S BODY
# IS WALKED AS CONSUMED.
#
# T3 row E-5 of the necessary-run walk (src/facts/req.c `rb_zero_rows`) makes
# a positive lookaround CAT's width-0 unit: the run joins ACROSS it and reads
# nothing of its body. This plant walks the body as if the subject consumed it
# there, so `xyz(?<=yz)abc` claims `xyzyzabc` and `(?<=foo)bar` claims
# `foobar` at offset 0; the pre-check then deletes their matches (a search of
# `foobar` from 3 finds no attempt). Detector: the harness on
# tests/litscan/spanarms.rxt (both engines).
SAB_ID="S1925-lookaround-body-walked-consumed"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC="the necessary-run walk reads a positive lookaround's body as consumed text instead of the width-0 unit, so its run claims the body's bytes at the cursor and the pre-check deletes matches"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sae2_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1925."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "xyz(?<=yz)abc" && grep -qE "^#define RX_REQ_RUN \"78797a616263@[0-9]\"$" "$REACH_TMP/o.c" && echo REACH-SL-RUN-JOINED'
SAB_REACH_EXPECT="REACH-SL-RUN-JOINED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    case RB_ZERO_UNIT: rb_zero_unit_into(w, acc); return;'
SAB_AFTER='    case RB_ZERO_UNIT: if (a->k == A_LOOK && !a->u.look.neg) { RbVal *v = pcrec_arena_alloc(&w->cx->arena, sizeof *v); rb_walk(w, a->l, v); rb_cat_into(w, acc, v); return; } rb_zero_unit_into(w, acc); return;   /* SABOTAGE S1925 */'
