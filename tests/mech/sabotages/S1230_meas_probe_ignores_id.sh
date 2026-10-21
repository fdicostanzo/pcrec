# S1230 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: an -I file whose header id differs from NAME is accepted as NAME (design S958, renumbered).
# Detector: the -I fixture: --measures=other over other.measures.tsv (id mine) must refuse naming the file.
SAB_ID="S1230-meas-probe-ignores-id"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='an -I file whose header id differs from NAME is accepted as NAME (design S958, renumbered)'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1230.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (strcmp(set->hdr[KS_MH_ID], name)) return KS_FILE_OTHER;'
SAB_AFTER='    if (0 && strcmp(set->hdr[KS_MH_ID], name)) return KS_FILE_OTHER;   /* SABOTAGE S1230 */'
