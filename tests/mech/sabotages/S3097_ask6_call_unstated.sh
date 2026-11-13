#!/usr/bin/env bash
# S3097 ([MEMFN] plan_frame.md 3.0b, row (AG), §4.2 ASK-6; lane b30b) -- ASK-6
# ASKS WITH CALL 0.
#
# WHAT IT BREAKS: req_run_at's cover-row phase-1 ask (ASK-6) passes call 0
# (UNSTATED), which the kit refuses. Before 3.0b a refused ask silently
# dropped the `@` of <PREFIX>_REQ_RUN; 3.0b makes the refusal LOUD: the
# compile fails with "the memfn kit refused the `@` table's cover-row phase-1
# ask". The reach probe pins a cover-routed pattern whose `@` comes from ASK-6.
SAB_ID="S3097-ask6-call-unstated"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC='ASK-6 (req_run_at'"'"'s cover-row ask) states call 0: the kit refuses it and the compile fails with ASK-6'"'"'s internal-error text on every cover-routed pattern with a REQ_RUN run'
SAB_DOC_FIGURE='Validated by plant at 3.0b (lane b30b): the planted pcrec refuses zqxzqx, hello world and abc[de]fghij (cover route) with the internal error naming req_run_at, and compiles a.*zqxzqx (no cover route). Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3097.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern zqxzqx && grep -q "^#define RX_DFA_SCAN \"cover\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_RUN \"7a71787a7178@3\"" "$REACH_TMP/o.c" && echo REACH-ASK6-COVER'
SAB_REACH_EXPECT="REACH-ASK6-COVER"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (mf_wdecide(pcrec_memfn_art(cx), cs, NULL, MF_WCALL_NONE, &w))'
SAB_AFTER='        if (mf_wdecide(pcrec_memfn_art(cx), cs, NULL, MF_WCALL_UNSTATED, &w))   /* SABOTAGE S3097 */'
