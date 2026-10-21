# S1228 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: --measures beats a target's measures config line: fill-only broken (design S946, renumbered).
# Detector: the fill-only fixture: a target whose config names zen4-grid1@1, compiled with --measures=./no-such-file.tsv, must compile under the file's value and print the note.
SAB_ID="S1228-meas-fill-only-flag-wins"
SAB_FILE="cli/main.c"
SAB_SUITES="knowledge"
SAB_DESC='--measures beats a target'"'"'s measures config line: fill-only broken (design S946, renumbered)'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1228.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        KsPick pk = pcrec_ks_pick(ts.opt.measures, t->measures);'
SAB_AFTER='        KsPick pk = pcrec_ks_pick(t->measures, ts.opt.measures);   /* SABOTAGE S1228 */'
