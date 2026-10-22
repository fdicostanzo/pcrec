# S1331 ([K113], lane k113) -- a compound part resolves the analysis chain from the inherited options instead of taking its walk's.
# Detector: tests/compound/run_part_analysis.sh (test-compound): a part's extra KSTRACE resolve record.
SAB_ID="S1331-part-chain-reresolves"
SAB_FILE="src/parse/rxt_find.c"
SAB_SUITES="compound"
SAB_DESC='a compound part resolves the analysis chain from the inherited options instead of taking its walk'"'"'s'
SAB_DOC_FIGURE='MEASURED by the lane solo (docs/dev/lanes/k113_report.md); exact re-run: bash tests/mech/run_sabotage_matrix.sh S1331.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    if (cx->emit_in && cx->emit_in->meas) {'
SAB_AFTER='    if (0 && cx->emit_in && cx->emit_in->meas) {   /* SABOTAGE S1331 */'
