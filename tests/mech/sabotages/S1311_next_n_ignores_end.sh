# S1311 -- [FINDALL-NEXT] I4 (lane i2build; docs/design/findall_iter_i2.md §5.4,
# docs/spec/match_api.md §3.8.1-§3.8.2). Old label: S939.
#
# Plant: _next_n's loop ignores the end: it runs __one k times whatever each returns, and returns k.
# Witness: N64 on the --step-budget=100 cells of (a+)+b, where the iterator gives up after >= 1 entry of the same call: count and rc against I.
# Reach (K35): reach token gumid (a call that returned 1..k-1 entries and then a code); tests/findall/run_iter_diff.sh fails a run where it is 0.
SAB_ID="S1311-next-n-ignores-end"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='the loop of _next_n ignores the end: it runs __one k times whatever each returns, and returns k'
SAB_DOC_FIGURE='Owed: lane i2build queued this row (docs/dev/lanes/i2build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1311.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    while (i < k && %s__one(it, capture_spans + i * %s_NCAPS))\n"'
SAB_AFTER='        "    while (i < k && (%s__one(it, capture_spans + i * %s_NCAPS) | (i < k)))   /* SABOTAGE S1311 */\n"'
