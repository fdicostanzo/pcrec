# S1321 -- [FINDALL-NEXT] I1 defect found at I4 (lane i2build; the gstart
# iterator arm, docs/dev/lanes/i2build_report.md; docs/spec/match_api.md §3.8¶2).
#
# Plant: the STEP no longer stops past the end (lo > n), so after an empty match at n
# a search runs at n + 1.
# Witness: the bare `\G` on the DFA (cells.tsv's `\G` group; tests/assertions/
# run_gstart_diff.sh §1b's `\G`): the attempt body reports an empty match at n + 1
# (outside the subject) forever, where libpcre2's global iteration ends.
# Reach (K35): the `\G` group compiles on the DFA arm (run_iter_diff.sh's groups).
SAB_ID="S1321-step-past-end-searches"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='the STEP no longer stops past the end, so after an empty match at n a search runs at n + 1'
SAB_DOC_FIGURE='Owed: lane i2build queued this row (docs/dev/lanes/i2build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1321.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    if (lo > n) { *at = lo; return 0; }   /* an empty match at n ended it */\n",'
SAB_AFTER='        "    /* SABOTAGE S1321 */\n",'
