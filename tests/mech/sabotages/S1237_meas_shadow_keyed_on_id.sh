# S1237 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: the shadow check is keyed on id alone: a FILE with a committed id at an uncommitted rev and the committed digest is accepted (design S988, renumbered).
# Detector: the shadow fixture rev7.tsv (zen4-grid1, rev 7, rev 1's digest) must refuse 'has no committed rev 7'.
SAB_ID="S1237-meas-shadow-keyed-on-id"
SAB_FILE="src/core/measures.c"
SAB_SUITES="knowledge"
SAB_DESC='the shadow check is keyed on id alone: a FILE with a committed id at an uncommitted rev and the committed digest is accepted (design S988, renumbered)'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1237.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    const KsMeasSet *same = store_find(id, strlen(id), set->rev);'
SAB_AFTER='    const KsMeasSet *same = store_find(id, strlen(id), 0);   /* SABOTAGE S1237 */'
