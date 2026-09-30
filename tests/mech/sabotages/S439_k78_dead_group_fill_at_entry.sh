# S439 (K78, lane k78) -- THE DEAD-GROUP FILL RUNS AT THE SEARCH ENTRY AGAIN.
#
# A DFA artifact with <PREFIX>_NCAPS >= 2 promises groups no match can set
# (reached only through a subroutine call, or under a {0}) and reports them
# PCREC_UNSET. Since abi 55 the fill is written on each success path, beside
# the caps[0] write. The plant also writes it at the top of <prefix>_search,
# the pre-K78 placement, so a no-match (and startpos > n) returns 0 with
# caps[1..NCAPS-1] overwritten, against match_api.md §3.1. Every RETURN value
# is unchanged and a success still writes every pair, so the corpus is green
# by construction; the detector is tests/codegen/run_nomatch_caps.sh (the
# dead-group witnesses' auto, -fno-anchored-dfa and -e utf8 routes, and the
# corpus slice's dead-group artifacts).
SAB_ID="S439-k78-dead-group-fill-at-entry"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="nomatchcaps"
SAB_DESC="emit_search_head writes the dead-group PCREC_UNSET fill at the search entry again (the pre-K78 placement), so a DFA dead-group artifact overwrites caps[1..] on a no-match"
SAB_DOC_FIGURE="Read the current figure from a run (lane k78 measured the detector against the pre-fix compiler: 4 of 7 checks red; docs/dev/lanes/k78_report.md)."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "(?(DEFINE)(?<x>\\b))b(?&x)"'
SAB_REACH_EXPECT='#define RX_NCAPS 2'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_emit_startpos_guard(cx, c, "    ", "search_from", "subject",
                                  "subject_length", false);
}'
SAB_AFTER='        pcrec_emit_startpos_guard(cx, c, "    ", "search_from", "subject",
                                  "subject_length", false);
    emit_dead_group_fill(cx, c, "    ");   /* SABOTAGE S439 */
}'
