#!/usr/bin/env bash
# S768 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- R2: the row is routed on CAND_ROUTE_ATTEMPT, which has no reverse machine and no walk emitter.
# Detector: an ENG_ATTEMPT end-pinned pattern (`^\w+$`, `(?m:^)\w+$`) selects `rev-end`: no emitter on that route (a crash) and the self-check's needs-unrouted.
SAB_ID='S768-revend-route-widened'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness candoracle'
SAB_DESC='R2: the row is routed on CAND_ROUTE_ATTEMPT, which has no reverse machine and no walk emitter'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S768.'
SAB_HARNESS_TARGET='tests/assertions'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "^\\w+$" && grep -qF "#define RX_DFA_SCAN \"attempt\"" "$REACH_TMP/o.c" && echo REACH-ATTEMPT'
SAB_REACH_EXPECT='REACH-ATTEMPT'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { .c = { "rev-end", PCREC_NO_REV_END, locate_rev_end_applies }, .slot = CAND_SLOT_LOCATE,
      .routes = CR_DFA, .tok = "rev-end", .map = CM_NONE,'
SAB_AFTER='    { .c = { "rev-end", PCREC_NO_REV_END, locate_rev_end_applies }, .slot = CAND_SLOT_LOCATE,
      .routes = CR_DFA | CR_ATTEMPT, .tok = "rev-end", .map = CM_NONE,   /* SABOTAGE S768 */'
