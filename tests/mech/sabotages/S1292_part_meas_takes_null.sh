# S1292 ([MEASURE-SET], lane partmeas) -- the walk hands a part no measurement set (NULL), so the part resolves its own and, under the harness lever, reads the default.
# Detector: tests/compound/run_part_measures.sh (test-compound), (A): under the lever a part is handed the default set, not P's.
SAB_ID="S1292-part-meas-takes-null"
SAB_FILE="src/core/compound.c"
SAB_SUITES="compound"
SAB_DESC='the walk hands a part no measurement set (NULL), so the part resolves its own and, under the harness lever, reads the default'
SAB_DOC_FIGURE='MEASURED by the lane solo (docs/dev/lanes/partmeas_report.md section 4); exact re-run: bash tests/mech/run_sabotage_matrix.sh S1292.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='                                &meas, &w->out[i],'
SAB_AFTER='                                NULL, &w->out[i],   /* SABOTAGE S1292 */'
