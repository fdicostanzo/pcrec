# S1238 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: the shadow check accepts a committed (id, rev) with other values, so a stamp would name values the store does not hold.
# Detector: the shadow fixture values.tsv (zen4-grid1@1, one value changed, digest recomputed) must refuse.
SAB_ID="S1238-meas-shadow-values-unchecked"
SAB_FILE="src/core/measures.c"
SAB_SUITES="knowledge"
SAB_DESC='the shadow check accepts a committed (id, rev) with other values, so a stamp would name values the store does not hold'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1238.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (same->digest == set->digest) return 0;'
SAB_AFTER='        return 0;   /* SABOTAGE S1238 */'
