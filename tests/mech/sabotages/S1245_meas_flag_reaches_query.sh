# S1245 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: --measures is no longer refused outside a compile: it rides a query silently.
# Detector: the reach check: --measures=zen4-grid1 --list-syntax must refuse.
SAB_ID="S1245-meas-flag-reaches-query"
SAB_FILE="cli/main.c"
SAB_SUITES="knowledge"
SAB_DESC='--measures is no longer refused outside a compile: it rides a query silently'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1245.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (st.opt.measures && !(st.nfiles || (st.pattern && m0 == 0))) {'
SAB_AFTER='        if (0 && st.opt.measures && !(st.nfiles || (st.pattern && m0 == 0))) {   /* SABOTAGE S1245 */'
