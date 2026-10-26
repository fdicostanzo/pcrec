# S1633 -- [SCANEDGE-SET] THE EMITTED RUN TEST COUNTS ONLY THE SET'S LOWEST
# CLASS.
#
# The pass (src/opt/scanedge.c) finds a run over a byte-class SET and the
# emitter's `scan_byte_set` turns the set into the run test's bytes. This plant
# keeps only the set's lowest class there: every unbounded set edge then stops
# at the first byte of another set class and the table step (its self-loop
# cell is intact) resumes the run, so NO ANSWER MOVES -- the edge just stops
# paying. Only check (1), the census's section (7), sees it: it holds the run
# test's bytes to the bytes whose transition stays on the head.
SAB_ID="S1633-scanset-run-test-lowest-class"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="scanedge"
SAB_DESC="scan_byte_set writes only the scan set's lowest class into the run test, so a multi-class unbounded edge stops at every byte of its other classes and the table walk resumes; answers are identical, run_scan_edge_census.sh section (7) must report the run test's bytes disagreeing with the head's stay row"
SAB_DOC_FIGURE="PREDICTED: scanedge RED (section (7) mismatch on the first multi-class artifact). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1633."
SAB_REACH='"$PCREC" -p rx --features all -fcomments -o /dev/stdout --pattern "\\S+@\\S+"'
SAB_REACH_EXPECT="SCAN EDGE: every state a run of classes 0, 2"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for (int b = 0; b < 256; b++) set[b] = (uint8_t)pcrec_scan_has(st, d->clsmap[b]);'
SAB_AFTER='    for (int b = 0; b < 256; b++) set[b] = (uint8_t)(d->clsmap[b] == scan_set_low(d, st));   /* SABOTAGE S1633 */'
