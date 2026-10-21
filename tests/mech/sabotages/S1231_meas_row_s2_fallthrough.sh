# S1231 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: the measures row's s2_mismatch is fallthrough-note: a mismatched -I file is skipped and the search goes on (design S985, renumbered).
# Detector: the -I fixture: --measures=other must refuse with 'defines no measurement set', not fall through to an unknown-name refusal.
SAB_ID="S1231-meas-row-s2-fallthrough"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='the measures row'"'"'s s2_mismatch is fallthrough-note: a mismatched -I file is skipped and the search goes on (design S985, renumbered)'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1231.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    .s2_mismatch   = KS_S2_REFUSE,'
SAB_AFTER='    .s2_mismatch   = KS_S2_FALLTHROUGH_NOTE,   /* SABOTAGE S1231 */'
