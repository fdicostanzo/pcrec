# S1634 -- [SCANEDGE-SET] THE SCAN-SHAPE RULE IS BACK TO ONE CLASS.
#
# `shaped()` puts into the set every class going where the key class goes.
# This plant admits the key class alone (the pre-[SCANEDGE-SET] rule): the
# other set classes then count as exits, the exit is not uniform, and every
# run the pattern splits into several classes loses its edge again -- the
# trimreg regression (`\s+$`, 0.19 -> 1.19 ns/B). No answer moves. Check (2),
# the census's section (8) witnesses, sees it per machine, and section (7)'s
# multi-class floor sees the population drop to 0.
SAB_ID="S1634-scanset-one-class-rule"
SAB_FILE="src/opt/scanedge.c"
SAB_SUITES="scanedge"
SAB_DESC="shaped() admits only the key class into the scan set, so \\S+@\\S+, \\s+\$, 0x[0-9a-fA-F]+ and reverse [a-z]+\\.txt\$ lose their multi-class edges; answers are identical, run_scan_edge_census.sh section (8)'s witness rows and section (7)'s multi-class floor must go red"
SAB_DOC_FIGURE="PREDICTED: scanedge RED (section (8) rows for the four multi-class witnesses, section (7) floor). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1634."
SAB_REACH='"$PCREC" -p rx --features all -fcomments -o /dev/stdout --pattern "0x[0-9a-fA-F]+"'
SAB_REACH_EXPECT="SCAN EDGE: every state a run of classes 1, 2"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (tr[c] == tr[cls]) {'
SAB_AFTER='        if (c == cls) {   /* SABOTAGE S1634 */'
