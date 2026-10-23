# S1309 -- [FINDALL-NEXT] I4 (lane i2build; docs/design/findall_iter_i2.md §5.4,
# docs/spec/match_api.md §3.8.1-§3.8.2). Old label: S938.
#
# Plant: _next_n's loop test is i <= k, so a call writes one entry past the k the caller provided.
# Witness: the N3 arm on a subject with >= 4 matches (`a` on a x 16), its entries buffer heap-allocated at exactly 3 * NCAPS pairs: an ASan error in the ASan cells, a stale or overrun entry and an over-count in the plain run.
# Reach (K35): reach token n3m4 (N3 cells with >= 4 matches); tests/findall/run_iter_diff.sh fails a run where it is 0.
SAB_ID="S1309-next-n-writes-entry-k"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='the loop test of _next_n is i <= k, so a call writes one entry past the k the caller provided'
SAB_DOC_FIGURE='Owed: lane i2build queued this row (docs/dev/lanes/i2build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1309.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    while (i < k && %s__one(it, capture_spans + i * %s_NCAPS))\n"'
SAB_AFTER='        "    while (i <= k && %s__one(it, capture_spans + i * %s_NCAPS))   /* SABOTAGE S1309 */\n"'
