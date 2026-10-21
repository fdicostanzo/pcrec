# S1233 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: the loader's refusal of a derived view's section is planted out (design S962, renumbered).
# Detector: the fed-back fixture: a decoded view given as --measures=FILE must refuse naming 'derived view'.
SAB_ID="S1233-meas-loader-accepts-derived"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='the loader'"'"'s refusal of a derived view'"'"'s section is planted out (design S962, renumbered)'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1233.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (in_list(meas_derived, NELEM(meas_derived) - 1, s->name))'
SAB_AFTER='        if (0 && in_list(meas_derived, NELEM(meas_derived) - 1, s->name))   /* SABOTAGE S1233 */'
