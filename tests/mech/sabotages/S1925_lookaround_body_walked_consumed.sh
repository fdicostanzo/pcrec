#!/usr/bin/env bash
# S1925 (lane sae2, 2026-11-09; span_arms E2, witness S-L,
# docs/design/span_arms.md §4.1 S16 and §5.7) -- A POSITIVE LOOKAROUND'S BODY
# IS WALKED AS CONSUMED.
#
# T3 row E-5i of the necessary-run walk (src/facts/req.c `rb_zero_rows`; span
# arms L1, re-aimed by lane l1feat 2026-11-19 from E2's E-5, which L1's E-5i
# row now precedes for every positive lookaround) makes a positive lookaround
# CAT's width-0 unit carrying its ITEM: the run joins ACROSS it and reads its
# body only as guards at their own offsets. This plant walks the body as if the subject consumed it
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
SAB_BEFORE='    case RB_ZERO_ITEM:  rb_zero_item_into(w, acc, a, t);           return;'
SAB_AFTER='    case RB_ZERO_ITEM:  if (a->k == A_LOOK) { RbVal *v = pcrec_arena_alloc(&w->cx->arena, sizeof *v); rb_walk(w, a->l, v); rb_cat_into(w, acc, v); return; } rb_zero_item_into(w, acc, a, t); return;   /* SABOTAGE S1925 */'
