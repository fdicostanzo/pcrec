# S1316 -- [FINDALL-NEXT] I4 (lane i2build; docs/design/findall_iter_i2.md §5.4,
# docs/spec/match_api.md §3.8.1-§3.8.2). Old label: new.
#
# Plant: RX_FOREACH's inner increment does not clear brk, so the body re-runs on one match and the loop never advances.
# Witness: F on any subject with >= 2 matches (iter_drv's MAXM cap ends the repeat); Fstop.
# Reach (K35): reach token f2 (F cells with >= 2 matches); tests/findall/run_iter_diff.sh fails a run where it is 0.
SAB_ID="S1316-foreach-brk-not-cleared"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='the RX_FOREACH inner increment does not clear brk, so the body re-runs on one match and the loop never advances'
SAB_DOC_FIGURE='Owed: lane i2build queued this row (docs/dev/lanes/i2build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1316.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "             rx_fp_##m_->brk; rx_fp_##m_->brk = 0)\n"'
SAB_AFTER='        "             rx_fp_##m_->brk; (void)0)   /* SABOTAGE S1316 */\n"'
