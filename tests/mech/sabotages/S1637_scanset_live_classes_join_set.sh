# S1637 -- [SCANEDGE-SET] TWO CLASSES GOING TO DIFFERENT SUCCESSORS JOIN ONE
# SET.
#
# The set rule's first clause is that every class of the set goes to the SAME
# successor. This plant lets any class with a live target join the key's set,
# so a state whose live classes go to DIFFERENT states (`([a-z]|[0-9]X){0,8}`,
# the negative control) can be called scan-shaped with the dead target as its
# exit. Check (2)'s negative row (census section (8)) is the detector: that
# pattern must keep NO edge on any machine.
SAB_ID="S1637-scanset-live-classes-join-set"
SAB_FILE="src/opt/scanedge.c"
SAB_SUITES="scanedge"
SAB_DESC="shaped() puts every class with a live target into the key class's set, so a state whose live classes go to different successors is scan-shaped over the dead exit; run_scan_edge_census.sh section (8)'s negative row ([a-z]|[0-9]X){0,8} must go red"
SAB_DOC_FIGURE="PREDICTED: scanedge RED (section (8) negative row, section (7) mismatches). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1637."
SAB_REACH='"$PCREC" -p rx --features all -fcomments -o /dev/stdout --pattern "([a-z]|[0-9]X){0,8}"'
SAB_REACH_EXPECT="rx_forward_byte_class"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (tr[c] == tr[cls]) {'
SAB_AFTER='        if (tr[c] == tr[cls] || (tr[c] >= 0 && tr[cls] >= 0)) {   /* SABOTAGE S1637 */'
