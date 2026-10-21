# S1239 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: the rows are kept in file order: the digest and the canonical view stop being in canonical (bytewise key) order.
# Detector: fx-messy (its rows out of order) no longer loads: its declared digest is over canonical order.
SAB_ID="S1239-meas-rows-unsorted"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='the rows are kept in file order: the digest and the canonical view stop being in canonical (bytewise key) order'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1239.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    qsort(rows, s->nrows, sizeof *rows, row_cmp);'
SAB_AFTER='    (void)row_cmp;   /* SABOTAGE S1239 */'
