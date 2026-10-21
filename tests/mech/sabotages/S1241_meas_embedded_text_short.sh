# S1241 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: the embedded store text is one byte short of the committed set file (a stale make gen-measures).
# Detector: meas_store_check.c's text = file compare.
SAB_ID="S1241-meas-embedded-text-short"
SAB_FILE="src/core/measures_store.inc"
SAB_SUITES="knowledge"
SAB_DESC='the embedded store text is one byte short of the committed set file (a stale make gen-measures)'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1241.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "zen4-grid1@1", pcrec_meas_store_text_0, 9562 },'
SAB_AFTER='    { "zen4-grid1@1", pcrec_meas_store_text_0, 9561 },   /* SABOTAGE S1241 */'
