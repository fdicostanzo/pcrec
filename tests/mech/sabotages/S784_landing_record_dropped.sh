#!/usr/bin/env bash
# S784 ([START-LANDING] SL2, lane slbuild; docs/design/start_landing.md §7.5 row 4; docs/dev/lanes/slbuild_report.md) -- the landing record dropped from the NEXT block's closer.
# Detector: run_start_landing.sh §1/§5 (a landing artifact's record, and its answers against the triple-deny build); the corpus harness.
SAB_ID='S784-landing-record-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='startlanding harness'
SAB_DESC='pf_close stops writing landing_position = scan_position, so every landing artifact reports search_from as the match start'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S784.'
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/o.c" --pattern "\\w+" && grep -q "landing_position = scan_position;" "$REACH_TMP/o.c" && echo REACH-RECORD'
SAB_REACH_EXPECT='REACH-RECORD'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (f->landing)
        pcrec_sb_printf(c, "%s    landing_position = %s;\n", ind, f->dir->posv);'
SAB_AFTER='    if (0 && f->landing)   /* SABOTAGE S784 */
        pcrec_sb_printf(c, "%s    landing_position = %s;\n", ind, f->dir->posv);'
