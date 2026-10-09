#!/usr/bin/env bash
# S686 ([MEMFN] R4e'.0, lane r4e0) -- fn_rows[]' BODY ROWS IN THE WRONG ORDER.
#
# WHAT IT BREAKS. The offset-skip function's body is the BODY slot of the
# first-match table `fn_rows[]` (memfn/src/ofsskip.c; integration.md
# §R4.9.2.1): `fn-pair` (the scanned position is a two-member cube) ABOVE
# `fn-memchr`, the slot's floor, whose predicate always holds. First match is
# what keeps the floor off a cube: the plant swaps the two rows, so the walk
# asks the floor first and every FUNC whose scanned position is a cube takes
# the one-stream memchr body on T, deleting every match that carries the other
# member there (`(?i)select` on "select" answers NOMATCH). The design's own
# plant for the seam's gate (integration.md §R4.9.8: "a plant swapping
# fn-pair/fn-memchr order is red on every two-cube FUNC").
#
# WHERE IT IS SEEN. The answers (reqcube.rxt's lowercase dispatch block, the
# S454 detector), and C5's pin of the `ofs-pair` fixture (arm memfnarms).
SAB_ID="S686-fn-rows-body-order-swapped"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="harness memfnarms"
SAB_HARNESS_TARGET="tests/litscan/reqcube.rxt"
SAB_DESC="fn_rows[]' BODY slot asks its floor (fn-memchr) before fn-pair, so a FUNC whose scanned position is a two-member cube scans one member and deletes the other's matches"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4e0 2026-10-09 (one mech row, solo): see docs/dev/lanes/r4e0_report.md §4. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S686."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "(?i)select"'
SAB_REACH_EXPECT='    size_t ha = 0, hb = 0;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# Re-aimed by lane r13 (R-13, 2026-10-09): its anchor moved with the R4e' batch 1 seam
# (kit_walk's per-row step / fn_rows[]'s decl column / the seam's level blocks); same intent.
SAB_BEFORE='    { FN_BODY, pair_holds,   pair_body,   &fn_pair_ct,   NULL },
    { FN_BODY, memchr_holds, memchr_body, &fn_memchr_ct, NULL },'
SAB_AFTER='    { FN_BODY, memchr_holds, memchr_body, &fn_memchr_ct, NULL },   /* SABOTAGE S686 */
    { FN_BODY, pair_holds,   pair_body,   &fn_pair_ct,   NULL },'
