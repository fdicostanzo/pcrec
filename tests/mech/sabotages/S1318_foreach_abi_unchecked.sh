# S1318 -- [FINDALL-NEXT] I4 (lane i2build; docs/design/findall_iter_i2.md §5.4,
# docs/spec/match_api.md §3.8.1-§3.8.2). Old label: new.
#
# Plant: rx_foreach_begin does not compare the record's abi with the header's.
# Witness: Fabi: RX_FOREACH over a copy of the record with abi + 1 must run no body and end with PCREC_ERR_ITER.
# Reach (K35): reach token fabi (every cell); tests/findall/run_iter_diff.sh fails a run where it is 0.
SAB_ID="S1318-foreach-abi-unchecked"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='rx_foreach_begin does not compare the abi of the record with the header abi'
SAB_DOC_FIGURE='Owed: lane i2build queued this row (docs/dev/lanes/i2build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1318.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    if (info->abi == PCREC_RX_ABI_H && info->next_n && info->ncaps > 0)\n"'
SAB_AFTER='        "    if (info->next_n && info->ncaps > 0)   /* SABOTAGE S1318 */\n"'
