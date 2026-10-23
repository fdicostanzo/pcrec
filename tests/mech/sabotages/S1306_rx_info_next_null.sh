# S1306 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: rx_info.next is NULL on every artifact.
# Detector: the info arm (rx_info.next must be the artifact's own <prefix>_next).
SAB_ID="S1306-rx-info-next-null"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="findall"
SAB_DESC='rx_info.next is NULL on every artifact'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1306.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, "    .next = %s_next,\n", cx->opt->prefix);'
SAB_AFTER='        pcrec_sb_printf(c, "    .next = NULL, /* %s SABOTAGE S1306 */\n", cx->opt->prefix);'
