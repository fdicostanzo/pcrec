# S1637 -- [SCANEDGE-SET] TWO CLASSES GOING TO DIFFERENT SUCCESSORS JOIN ONE
# SET.
#
# The set rule's first clause is that every class of the set goes to the SAME
# successor. This plant lets any class with a live target join the key's set,
# so a state whose live classes go to DIFFERENT states (`(?:a|bc)*`'s start
# state: `a` stays, `b` leaves) is called scan-shaped with the dead target as
# its exit. Check (2)'s negative row (census section (8)) is the detector: that
# pattern must keep NO edge on any machine. MEASURED by hand: the plant gives
# it forward, anchored and retry edges; `(?:[a-z]|[0-9]X){0,8}` keeps none
# under the plant (its chains fail the in-degree test), so it is NOT the
# witness.
SAB_ID="S1637-scanset-live-classes-join-set"
SAB_FILE="src/opt/scanedge.c"
SAB_SUITES="scanedge"
SAB_DESC="shaped() puts every class with a live target into the key class's set, so a state whose live classes go to different successors is scan-shaped over the dead exit; run_scan_edge_census.sh section (8)'s negative row (?:a|bc)* must go red"
SAB_DOC_FIGURE="PREDICTED: scanedge RED (section (8) negative row, section (7) mismatches). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1637."
SAB_REACH='"$PCREC" -p rx --features all -fcomments -o /dev/stdout --pattern "(?:a|bc)*"'
SAB_REACH_EXPECT="rx_forward_byte_class"
# (the artifact is a DFA with a forward machine, i.e. the shape the plant reaches)
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (tr[c] == tr[cls]) {'
SAB_AFTER='        if (tr[c] == tr[cls] || (tr[c] >= 0 && tr[cls] >= 0)) {   /* SABOTAGE S1637 */'
