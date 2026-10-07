#!/usr/bin/env bash
# S454 ([OPT-LITSCAN] S4 C3, lane c3build) -- THE BLOCK'S DISPATCH TESTS THE
# MEMCHR ARM FIRST.
#
# `ofs_test_run` sets `scan_byte` for every run, so `scan_byte >= 0` is always
# true and the pair arm must be tested BEFORE it (litscan_s4.md §2.3.4, r2
# R2-S2). This plant makes the pair test unreachable, so a masked scan
# position takes the memchr arm, scans T alone and deletes every match
# carrying the lower member there: `(?i)select` on "select" answers NOMATCH.
# An all-uppercase subject cannot see it. Detector: the harness on
# reqcube.rxt's lowercase dispatch block, and reqcube_check.py's two-memchr
# check. (Design's provisional S453.)
# RE-AIMED 2026-10-06 ([MEMFN] R4c REPLACE, lane r4ccore): the pair dispatch is the kit's offset-skip function (ofs_fn_define); the search text moved into the kit; the plant is the same defect in the kit's transcription of the form.
SAB_ID="S454-pair-dispatch-memchr-first"
SAB_FILE='memfn/src/ofsskip.c'
SAB_SUITES="harness codegen"
SAB_HARNESS_TARGET="tests/litscan/reqcube.rxt"
SAB_DESC="the run block's dispatch never reaches the pair arm, so a masked scan position takes the one-stream memchr arm on T and every lowercase match there is deleted"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/c3build_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S454."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?i)select" && grep -q "^#define RX_REQ_RUN \"53454c454354@4/dfdfdfdfdfdf\"" "$REACH_TMP/o.c" && grep -q "ha < pos + 4" "$REACH_TMP/o.c" && echo REACH-PAIR-ARM'
SAB_REACH_EXPECT="REACH-PAIR-ARM"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (b >= 0)
        return pair_body(art, h, p, pidx, maxk, k, a, b, o);'
SAB_AFTER='    if (0 && b >= 0)   /* SABOTAGE S454 */
        return pair_body(art, h, p, pidx, maxk, k, a, b, o);'
