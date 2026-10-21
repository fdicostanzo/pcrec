# S1293 ([MEASURE-SET], lane partmeas) -- the shell's MEASURES stamp ignores its parts' consulted bit (the union over P and the parts dropped).
# Detector: tests/compound/run_part_measures.sh (test-compound), (B): a consulting part leaves the shell stamping "".
SAB_ID="S1293-meas-stamp-drops-parts"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="compound"
SAB_DESC='the shell'"'"'s MEASURES stamp ignores its parts'"'"' consulted bit (the union over P and the parts dropped)'
SAB_DOC_FIGURE='MEASURED by the lane solo (docs/dev/lanes/partmeas_report.md section 4); exact re-run: bash tests/mech/run_sabotage_matrix.sh S1293.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='        if (sh->text[i]) consulted = consulted || sh->facts[i].meas_consulted;'
SAB_AFTER='        ;   /* SABOTAGE S1293 */'
