# S1244 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: the values digest hashes its domain without the terminating NUL (12 bytes for 13).
# Detector: every fixture's load (declared digests no longer match) and R5's digest against ks_ref.py.
SAB_ID="S1244-meas-domain-without-nul"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='the values digest hashes its domain without the terminating NUL (12 bytes for 13)'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1244.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    KS_DOMAIN("pcrec-meas-1"), KS_SUB_NONE, meas_fold'
SAB_AFTER='    (const unsigned char *)"pcrec-meas-1", 12, KS_SUB_NONE, meas_fold   /* SABOTAGE S1244 */'
