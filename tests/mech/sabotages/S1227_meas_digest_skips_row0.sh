# S1227 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: values_digest folds row 0's value as 0: a set whose rows differ only in that value hashes alike (design S943, renumbered).
# Detector: R5 (the decoded view's recomputed digest against ks_ref.py's) on the store set and every fixture, and every fixture's load (its declared digest no longer matches).
SAB_ID="S1227-meas-digest-skips-row0"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='values_digest folds row 0'"'"'s value as 0: a set whose rows differ only in that value hashes alike (design S943, renumbered)'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1227.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        uint64_t v = (uint64_t)r->value_e6;'
SAB_AFTER='        uint64_t v = i ? (uint64_t)r->value_e6 : 0;   /* SABOTAGE S1227 */'
