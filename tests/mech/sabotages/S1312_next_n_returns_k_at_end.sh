# S1312 -- [FINDALL-NEXT] I4 (lane i2build; docs/design/findall_iter_i2.md §5.4,
# docs/spec/match_api.md §3.8.1-§3.8.2). Old label: new.
#
# Plant: _next_n returns k on the end path, so the entries after the end are stale and the caller never sees the end.
# Witness: N64 and F on a subject with 1..63 matches that ends by done.
# Reach (K35): reach token done63 (done cells with 1..63 matches); tests/findall/run_iter_diff.sh fails a run where it is 0.
SAB_ID="S1312-next-n-returns-k-at-end"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='_next_n returns k on the end path, so the entries after the end are stale and the caller never sees the end'
SAB_DOC_FIGURE='Owed: lane i2build queued this row (docs/dev/lanes/i2build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1312.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    return i;\n"'
SAB_AFTER='        "    return i < k ? k : i;   /* SABOTAGE S1312 */\n"'
