# S1240 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: rx_info.measures is written with other text than <PREFIX>_MEASURES (the mirror is no longer byte for byte).
# Detector: the default-compile check: .measures's initializer must equal the macro's value.
SAB_ID="S1240-meas-mirror-differs"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="knowledge"
SAB_DESC='rx_info.measures is written with other text than <PREFIX>_MEASURES (the mirror is no longer byte for byte)'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1240.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    emit_ks_line(cx, c, m, "MEASURES", "measures", value);'
SAB_AFTER='    emit_ks_line(cx, c, m, "MEASURES", "measures", m == PCREC_KS_MARK_INIT ? "x" : value);   /* SABOTAGE S1240 */'
