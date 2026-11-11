#!/usr/bin/env bash
# S3042 ([MEMFN] R-38 K38-2, lane k382) -- THE REQ_RUN STAMP'S `@` IS
# PCREC'S OWN INDEX, NOT THE SEARCHING SITE'S.
#
# WHAT IT BREAKS. span_runs_sheet.md §4.1 / §2.4 C4: `<PREFIX>_REQ_RUN`'s `@`
# is a first-match table (the pre-check's run reply's scan, else the
# cover/run-pinned window site's member, else none), never pcrec's
# `req_run` fact index (`pcrec_fact_req_run_stated(cx)->idx`). The plant
# feeds the stamp pcrec's index. Default builds agree on most witnesses (both
# tie rightmost), so the detector is reqcube_check.py's C4 lever rows: under
# the harness lever `run-tie-left` the kit's scan is the LEFTMOST tie while
# pcrec's index stays rightmost, and the stamp's `@` must equal the run
# block's scan offset.
SAB_ID="S3042-req-run-at-is-pcrec-index"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="the REQ_RUN stamp's @ is pcrec's req_run index instead of the searching site's (the kit's run reply scan), so under a kit tie rule that differs from pcrec's the stamp names an offset the artifact's search does not read (C4)"
SAB_DOC_FIGURE="Validated by plant at K38-2 (docs/dev/lanes/k382_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3042."
# Reach: the lever witness's kit scan (@0) differs from pcrec's index (@3).
SAB_REACH='"$(dirname "$PCREC")/pcrec-harness" --harness=run-tie-left --memfn=no-window-search --features all -p rx -o "$REACH_TMP/o.c" --pattern "a.*zqxzqx" && grep -q "^#define RX_REQ_RUN \"7a71787a7178@0\"" "$REACH_TMP/o.c" && "$PCREC" --features all --emit-facts --pattern "a.*zqxzqx" 2>/dev/null | grep -q "req_run.*7a71787a7178@3" && echo REACH-C4-DIFFERS'
SAB_REACH_EXPECT="REACH-C4-DIFFERS"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                       pcrec_fact_stamp_req_run(cx, req_run_at(cx, admit)));'
SAB_AFTER='                       pcrec_fact_stamp_req_run(cx, pcrec_fact_req_run_stated(cx)->idx));   /* SABOTAGE S3042 */'
