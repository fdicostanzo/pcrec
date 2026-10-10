#!/usr/bin/env bash
# S789 ([START-LANDING] SL2, lane slbuild; docs/design/start_landing.md §7.5 row 12; docs/dev/lanes/slbuild_report.md) -- the guard's skip made O(K) per stepped byte (the cost shape of revision 1's restart, which re-entered the scan).
# Detector: run_start_landing.sh §H: find-all over 1 MiB of C3 then `a` within 10 s.
SAB_ID='S789-landing-guard-quadratic'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='startlanding'
SAB_DESC='every byte the guard steps over re-walks the rest of the excursion, so a hostile run of K lead bytes costs O(K^2): the bound revision 2'\''s post-loop skip exists to keep'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S789.'
SAB_REACH='"$PCREC" -e utf8 -p rx -o "$REACH_TMP/o.c" --pattern "." && grep -q "do landing_position++;" "$REACH_TMP/o.c" && echo REACH-GUARD'
SAB_REACH_EXPECT='REACH-GUARD'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                "            do landing_position++;\n"'
SAB_AFTER='                "            do { landing_position++; for (size_t rx_q = landing_position; rx_q < last_accept_position; rx_q++) __asm__ volatile(\"\" :: \"r\"(subject[rx_q])); }   /* SABOTAGE S789 */\n"'
