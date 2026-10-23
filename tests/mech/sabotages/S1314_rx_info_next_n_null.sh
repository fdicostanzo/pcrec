# S1314 -- [FINDALL-NEXT] I4 (lane i2build; docs/design/findall_iter_i2.md §5.4,
# docs/spec/match_api.md §3.8.1-§3.8.2). Old label: as S1306 for next.
#
# Plant: rx_info.next_n is NULL on every artifact.
# Witness: the info arm (rx_info.next_n must be <prefix>_next_n); GN, the plain loop over info->next_n (iter_drv.c gn_drain), which has no entry to call.
# Reach (K35): reach token g1 (artifacts that define next with >= 1 match); tests/findall/run_iter_diff.sh fails a run where it is 0.
SAB_ID="S1314-rx-info-next-n-null"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="findall"
SAB_DESC='rx_info.next_n is NULL on every artifact'
SAB_DOC_FIGURE='Owed: lane i2build queued this row (docs/dev/lanes/i2build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1314.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, "    .next = %s_next,\n    .next_n = %s_next_n,\n",'
SAB_AFTER='        pcrec_sb_printf(c, "    .next = %s_next,\n    .next_n = NULL, /* %s SABOTAGE S1314 */\n",'
