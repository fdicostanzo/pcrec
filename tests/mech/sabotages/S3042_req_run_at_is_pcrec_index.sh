#!/usr/bin/env bash
# S3042 ([MEMFN] R-38 K38-2, lane k382) -- THE REQ_RUN STAMP'S `@` IS
# PCREC'S OWN INDEX, NOT THE SEARCHING SITE'S.
#
# WHAT IT BREAKS. span_runs_sheet.md §4.1 / §2.4 C4: `<PREFIX>_REQ_RUN`'s `@`
# is a first-match table (the pre-check's run reply's scan, else the
# cover/run-pinned window site's member, else none), never pcrec's own
# pick over the run (`pcrec_find_run_scan_index`, the `req_byte` fact's
# input; the `req_run` row and its `@idx` retired, review 2026-11-11 r1 k382
# F5, re-aimed by lane k382fix). The plant makes `req_run_at` answer
# pcrec's own index. Default builds agree on most witnesses (both
# tie rightmost), so the detector is reqcube_check.py's C4 lever rows: under
# the harness lever `run-tie-left` the kit's scan is the LEFTMOST tie while
# pcrec's index stays rightmost, and the stamp's `@` must equal the run
# block's scan offset.
SAB_ID="S3042-req-run-at-is-pcrec-index"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="the REQ_RUN stamp's @ is pcrec's own pick over the run (the retired req_run row's index) instead of the searching site's (the kit's run reply scan), so under a kit tie rule that differs from pcrec's the stamp names an offset the artifact's search does not read (C4)"
SAB_DOC_FIGURE="Validated by plant at K38-2 (docs/dev/lanes/k382_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3042."
# Reach: the lever witness's kit scan (@0) differs from pcrec's index (@3,
# the default build's scan: both tie rightmost there).
SAB_REACH='"$(dirname "$PCREC")/pcrec-harness" --harness=run-tie-left --memfn=no-window-search --features all -p rx -o "$REACH_TMP/o.c" --pattern "a.*zqxzqx" && grep -q "^#define RX_REQ_RUN \"7a71787a7178@0\"" "$REACH_TMP/o.c" && "$PCREC" --memfn=no-window-search --features all -p rx -o "$REACH_TMP/d.c" --pattern "a.*zqxzqx" && grep -q "^#define RX_REQ_RUN \"7a71787a7178@3\"" "$REACH_TMP/d.c" && echo REACH-C4-DIFFERS'
SAB_REACH_EXPECT="REACH-C4-DIFFERS"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (pcrec_fact_req_whole_run_stated(cx)->whole_len < 2) return -1;
    if (req_admit_emits(admit)) {'
SAB_AFTER='    if (pcrec_fact_req_whole_run_stated(cx)->whole_len < 2) return -1;
    { const ReqRun *r_ = pcrec_fact_req_whole_run_stated(cx);   /* SABOTAGE S3042 */
      return pcrec_find_run_scan_index(pcrec_find_byte_rate(cx), r_->whole, r_->whole_mask, r_->whole_len); }
    if (req_admit_emits(admit)) {'
