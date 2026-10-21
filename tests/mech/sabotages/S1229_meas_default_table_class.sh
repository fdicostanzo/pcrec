# S1229 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: the generated default-pointer table names another class than measure_store/DEFAULTS (design S947, renumbered).
# Detector: DEFAULTS read by awk against --list-measurements' default_for column.
SAB_ID="S1229-meas-default-table-class"
SAB_FILE="src/core/measures_table.inc"
SAB_SUITES="knowledge"
SAB_DESC='the generated default-pointer table names another class than measure_store/DEFAULTS (design S947, renumbered)'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1229.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "idk", "zen4-grid1", 1u },'
SAB_AFTER='    { "jdk", "zen4-grid1", 1u },   /* SABOTAGE S1229 */'
