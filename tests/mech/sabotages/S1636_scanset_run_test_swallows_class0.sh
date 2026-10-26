# S1636 -- [SCANEDGE-SET] THE EMITTED RUN TEST ALSO COUNTS CLASS 0.
#
# The run test's bytes gain every byte of class 0, which on the set witnesses
# is the run's EXIT class (`\s+$`'s non-space bytes, `[a-z]+\.txt$`'s
# non-letters): the scan runs over bytes the machine leaves on, and spans
# move. Check (3), answer identity, is the detector: the new corpus file
# tests/classes/scan_set.rxt (libpcre2-8 10.46 expectations) must fail.
SAB_ID="S1636-scanset-run-test-swallows-class0"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/classes/scan_set.rxt"
SAB_DESC="scan_byte_set adds class 0's bytes to every edge's run test, so a scan passes bytes the machine exits on; tests/classes/scan_set.rxt must report wrong spans / lost matches against its libpcre2 expectations"
SAB_DOC_FIGURE="PREDICTED: corpus RED on tests/classes/scan_set.rxt. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1636."
SAB_REACH='grep -c "^pattern" "$TREE/tests/classes/scan_set.rxt"'
SAB_REACH_EXPECT="8"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for (int b = 0; b < 256; b++) set[b] = (uint8_t)pcrec_scan_has(st, d->clsmap[b]);'
SAB_AFTER='    for (int b = 0; b < 256; b++) set[b] = (uint8_t)(pcrec_scan_has(st, d->clsmap[b]) || d->clsmap[b] == 0);   /* SABOTAGE S1636 */'
