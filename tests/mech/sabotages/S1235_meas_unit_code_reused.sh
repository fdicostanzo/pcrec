# S1235 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: the code table gives walkbytes another byte, so every digest over a walkbytes row moves.
# Detector: the store set as a FILE is refused (its declared digest), and R5's unit_code and digest disagree with ks_ref.py's spec table.
SAB_ID="S1235-meas-unit-code-reused"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='the code table gives walkbytes another byte, so every digest over a walkbytes row moves'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1235.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "ratio", 0x01 }, { "walkbytes", 0x02 }, { "bytes", 0x03 }, { "count", 0x04 },'
SAB_AFTER='    { "ratio", 0x01 }, { "walkbytes", 0x05 }, { "bytes", 0x03 }, { "count", 0x04 },   /* SABOTAGE S1235 */'
