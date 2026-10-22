# S1332 ([K113], lane k113) -- a compound part builds its own analysis object instead of taking its walk's.
# Detector: tests/compound/run_part_analysis.sh (test-compound): a part's extra KSRCTRACE object lines.
SAB_ID="S1332-part-analysis-rebuilt"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="compound"
SAB_DESC='a compound part builds its own analysis object instead of taking its walk'"'"'s'
SAB_DOC_FIGURE='MEASURED by the lane solo (docs/dev/lanes/k113_report.md); exact re-run: bash tests/mech/run_sabotage_matrix.sh S1332.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    if (cx->emit_in && cx->emit_in->meas) {'
SAB_AFTER='    if (0 && cx->emit_in && cx->emit_in->meas) {   /* SABOTAGE S1332 */'
