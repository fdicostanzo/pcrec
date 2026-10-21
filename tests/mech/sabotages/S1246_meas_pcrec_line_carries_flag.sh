# S1246 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: a config's pcrec line may carry --measures (the refusal is planted out), so the set is chosen invisibly to the file's own measures line.
# Detector: the fixture h.rxt (config c: pcrec --measures=zen4-grid1) must refuse naming 'may not carry --measures'.
SAB_ID="S1246-meas-pcrec-line-carries-flag"
SAB_FILE="src/parse/rxt_source.c"
SAB_SUITES="knowledge"
SAB_DESC='a config'"'"'s pcrec line may carry --measures (the refusal is planted out), so the set is chosen invisibly to the file'"'"'s own measures line'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1246.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if ((n == 10 && !strncmp(w, "--measures", 10)) ||
            (n > 10 && !strncmp(w, "--measures=", 11)))'
SAB_AFTER='        if (0)   /* SABOTAGE S1246 */'
