# S1232 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: the canonical writer omits the cells section: R1 (values only) and R2 (the re-listing omits it again) stay green (design S961, renumbered).
# Detector: R3 on fx-rich (ks_ref.py reads the file and its canonical view as different documents) and R4 on the store (its file carries the section header).
SAB_ID="S1232-meas-canonical-drops-cells"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='the canonical writer omits the cells section: R1 (values only) and R2 (the re-listing omits it again) stay green (design S961, renumbered)'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1232.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    rc = rc || put_tab(o, "cells", cell_cols, KS_MEAS_NCELL, &set->cells) ||'
SAB_AFTER='    rc = rc || /* SABOTAGE S1232 */'
