# S1236 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: the section-TSV reader stops checking a row's field count against its header (table_contract.md §5¶1).
# Detector: the bad/fieldcount fixture must refuse with 'fields where section'.
SAB_ID="S1236-ks-tsv-field-count-unchecked"
SAB_FILE="src/core/ksrc.c"
SAB_SUITES="knowledge"
SAB_DESC='the section-TSV reader stops checking a row'"'"'s field count against its header (table_contract.md §5¶1)'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1236.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (got != o.s.ncols) {'
SAB_AFTER='            if (0 && got != o.s.ncols) {   /* SABOTAGE S1236 */'
