# S1295 ([MEASURE-SET], lane partmeas) -- a part's facts report its measurement set never consulted, so the shell's union cannot see it.
# Detector: tests/compound/run_part_measures.sh (test-compound), (B): a consulting part leaves the shell stamping "".
SAB_ID="S1295-part-facts-drop-meas-consult"
SAB_FILE="src/core/compile.c"
SAB_SUITES="compound"
SAB_DESC='a part'"'"'s facts report its measurement set never consulted, so the shell'"'"'s union cannot see it'
SAB_DOC_FIGURE='MEASURED by the lane solo (docs/dev/lanes/partmeas_report.md section 4); exact re-run: bash tests/mech/run_sabotage_matrix.sh S1295.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            pf->meas_consulted = meas_union || cx.job->meas_consulted;'
SAB_AFTER='            pf->meas_consulted = false;   /* SABOTAGE S1295 */'
