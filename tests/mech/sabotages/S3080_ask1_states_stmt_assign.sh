#!/usr/bin/env bash
# S3080 ([MEMFN] plan_frame.md 3.0b, row (F); lane b30b) -- ASK-1 STATES STMT/ASSIGN.
#
# WHAT IT BREAKS: window_reply_ask (ASK-1) states the offset-skip site as
# STMT/ASSIGN, while the define (ofs_site_define) states FUNC/RETURN. ASK-3's
# PCREC_CAND_TRACE re-ask at the define compares the WHOLE reply and fails as
# `asked-plan-differs` on every DFA prefilter witness the ASK-4 suite compiles.
# [rev2.2 R17]: the row's claim is that TEXT, not "the suite is red" (a
# refused framed ask would fail as window_reply_ask's own internal error,
# proving nothing about ASK-3). mech scores the suite; the text was verified
# by hand at the build: all 11 failing witnesses print CANDORACLE
# asked-plan-differs, none a refusal (b30b_report.md, Sabotage rows).
SAB_ID="S3080-ask1-states-stmt-assign"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="candoracle"
SAB_DESC='ASK-1'"'"'s phase-1 ask states STMT/ASSIGN where the define states FUNC/RETURN: ASK-3'"'"'s re-ask at ofs_site_define fails as asked-plan-differs (run_cand_oracle.sh'"'"'s CANDORACLE line)'
SAB_DOC_FIGURE='Validated by plant at 3.0b (lane b30b): a -DPCREC_CAND_TRACE build of the planted tree fails 11 of the 90 witness lines, every one CANDORACLE asked-plan-differs. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3080.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    s->pred.fn_ref = 1;
    pcrec_memfn_window_stated(cx, s, walts, n, MF_WFLOOR_SUBJECT);'
SAB_AFTER='    s->pred.fn_ref = 1;
    s->form = MF_FORM_STMT; s->handoff = MF_H_ASSIGN; s->pred.fn_ref = 0;   /* SABOTAGE S3080 */
    pcrec_memfn_window_stated(cx, s, walts, n, MF_WFLOOR_SUBJECT);'
