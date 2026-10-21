# S1300 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: after a non-empty match the iterator resumes at its end, not at the aligned end (K75).
# Detector: a utf8 match ending before a stray continuation byte: the iterator answers neither libpcre2 nor the loop.
SAB_ID="S1300-step-end-not-aligned"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='after a non-empty match the iterator resumes at its end, not at the aligned end (K75)'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1300.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            "        it->lo = %s__next_pos(s, n, (size_t)c[0][1] - 1);   /* K75: the aligned end */\n"'
SAB_AFTER='            "        it->lo = (size_t)c[0][1]; (void)%s__next_pos;   /* SABOTAGE S1300 */\n"'
