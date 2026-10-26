# S1635 -- [SCANEDGE-SET] THE ONE-CLASS EDGE'S EMITTED TEXT MOVES.
#
# A one-class edge is the set of size one, and its emitted text is promised
# unchanged by the generalization (the abi changelog's 86 -> 87 entry says
# so). This plant names every set in the plural, so `[a-z]+$`'s edge comment
# reads "classes 1": no answer moves and no stamp moves; only the census's
# section (8) control pin sees it.
SAB_ID="S1635-scanset-control-text-moves"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="scanedge"
SAB_DESC="scan_set_text always writes 'classes', so the one-class control [a-z]+\$'s edge comment moves to 'classes 1'; answers identical, run_scan_edge_census.sh section (8)'s control pin must go red"
SAB_DOC_FIGURE="PREDICTED: scanedge RED (section (8) control pin). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1635."
SAB_REACH='"$PCREC" -p rx --features all -fcomments -o /dev/stdout --pattern "[a-z]+\$"'
SAB_REACH_EXPECT="SCAN EDGE: every state a run of class 1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    const char *text = pcrec_sb_fragf(&cx->arena, "class%s %s", k > 1 ? "es" : "",'
SAB_AFTER='    const char *text = pcrec_sb_fragf(&cx->arena, "class%s %s", k > 0 ? "es" : "",   /* SABOTAGE S1635 */'
