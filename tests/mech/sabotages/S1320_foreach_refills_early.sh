# S1320 -- [FINDALL-NEXT] I4 (lane i2build; docs/design/findall_iter_i2.md §5.4,
# docs/spec/match_api.md §3.8.1-§3.8.2). Old label: new.
#
# Plant: rx_foreach_pull refills one entry early, dropping the last entry of every fill.
# Witness: F on any subject with >= 2 matches; Fstop at the batch ends j = 1, 3, 7.
# Reach (K35): reach tokens f2 and fstopend; tests/findall/run_iter_diff.sh fails a run where it is 0.
SAB_ID="S1320-foreach-refills-early"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='rx_foreach_pull refills one entry early, dropping the last entry of every fill'
SAB_DOC_FIGURE='Owed: lane i2build queued this row (docs/dev/lanes/i2build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1320.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    if (f->head == f->count) {\n"'
SAB_AFTER='        "    if (f->head + 1 >= f->count) {   /* SABOTAGE S1320 */\n"'
