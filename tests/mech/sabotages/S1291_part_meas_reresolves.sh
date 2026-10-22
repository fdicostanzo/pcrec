# S1291 ([MEASURE-SET], lane partmeas) -- a compound part resolves its own measurement set from the inherited options instead of taking its walk's.
# Detector: tests/compound/run_part_measures.sh (test-compound), (A): a part's loaded set is another object than P's.
SAB_ID="S1291-part-meas-reresolves"
SAB_FILE="src/core/measures.c"
SAB_SUITES="compound"
SAB_DESC='a compound part resolves its own measurement set from the inherited options instead of taking its walk'"'"'s'
SAB_DOC_FIGURE='MEASURED by the lane solo (docs/dev/lanes/partmeas_report.md section 4); exact re-run: bash tests/mech/run_sabotage_matrix.sh S1291.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    if (cx->emit_in && cx->emit_in->meas) {'
SAB_AFTER='    if (0 && cx->emit_in && cx->emit_in->meas) {   /* SABOTAGE S1291 */'
