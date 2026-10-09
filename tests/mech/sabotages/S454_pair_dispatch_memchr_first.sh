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
# RE-AIMED 2026-10-07 ([MEMFN] M1b REPLACE, lane m1b): `pidx` left the
# offset-skip function's parameters (no hook takes a term id once the run
# compare is the kit's), so the anchor's call loses it. Plant and intent
# unchanged.
# RE-AIMED 2026-10-09 ([MEMFN] R4e'.0, lane r4e0): the inline `if (b >= 0)`
# dispatch became the BODY slot of `fn_rows[]` (integration.md §R4.9.2.1):
# row `fn-pair` (predicate `b >= 0`) above `fn-memchr`, the slot's floor. The
# plant makes fn-pair's predicate never hold, so the walk falls to the floor:
# the same defect (a masked scan position takes the one-stream memchr body on
# T) at its new home. Intent and detectors unchanged.
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
SAB_BEFORE='    return x->b >= 0;'
SAB_AFTER='    return 0 && x->b >= 0;   /* SABOTAGE S454 */'
