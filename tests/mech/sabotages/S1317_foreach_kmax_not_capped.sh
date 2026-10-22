# S1317 -- [FINDALL-NEXT] I4 (lane i2build; docs/design/findall_iter_i2.md §5.4,
# docs/spec/match_api.md §3.8.1-§3.8.2). Old label: S1016.
#
# Plant: RX_FOREACH's kmax is not capped by RX_FOREACH_PAIRS / ncaps, so a fill can write past the macro's buffer.
# Witness: the ASan cells' -DRX_FOREACH_PAIRS=8 build: the 3-group cell (NCAPS 4, kmax 2) with >= 6 matches writes a third fill's 4 entries (16 pairs) past the buffer, the struct's last member; the 10-group cell is no longer refused (F).
# Reach (K35): reach tokens kmaxcap (kmax < 64 with >= 3 matches) and frefused, both in the ASan run; tests/findall/run_iter_diff.sh fails a run where it is 0.
SAB_ID="S1317-foreach-kmax-not-capped"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='the RX_FOREACH kmax is not capped by RX_FOREACH_PAIRS / ncaps, so a fill can write past the macro buffer'
SAB_DOC_FIGURE='Owed: lane i2build queued this row (docs/dev/lanes/i2build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1317.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    f->kmax = nc ? RX_FOREACH_PAIRS / nc : 0;\n"'
SAB_AFTER='        "    f->kmax = nc ? 64 : 0;   /* SABOTAGE S1317 */\n"'
