#!/usr/bin/env bash
# S1915 (lane sar1, 2026-11-09; span_arms R1, witness W-R1, docs/design/span_arms.md §3.6) -- T2 ROW 3 SETS `all`.
#
# T2 row 3 of the necessary-run walk's repeat table (src/facts/req.c
# `rr_rep_split`) reads a variable repeat `X{m,n}` as `X^m` then a gap, so it
# is never `all`: the bytes after it are not adjacent to its copies in every
# match. This plant sets `all`, so `xy(?:ab){1,2}zw` claims `xyabzw` and the
# pre-check deletes every match that takes two copies. Detector: the harness
# on tests/litscan/spanarms.rxt (both engines).
SAB_ID="S1915-rep-split-sets-all"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_DESC="the necessary-run walk's variable-repeat row marks the repeat as an exact literal, so the run joins its first copy to what follows and the pre-check deletes the matches that take more copies"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sar1_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1915."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "xy(?:ab){1,2}zw" && grep -qE "^#define RX_REQ_RUN \"61627a77@[0-9]+\"$" "$REACH_TMP/o.c" && echo REACH-WR1-RUN'
SAB_REACH_EXPECT="REACH-WR1-RUN"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    o.tail = rr_cat(gap, p).tail;'
SAB_AFTER='    o.tail = rr_cat(gap, p).tail; o.all = true;   /* SABOTAGE S1915 */'
