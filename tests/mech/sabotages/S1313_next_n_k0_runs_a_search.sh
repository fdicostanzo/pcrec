# S1313 -- [FINDALL-NEXT] I4 (lane i2build; docs/design/findall_iter_i2.md §5.4,
# docs/spec/match_api.md §3.8.1-§3.8.2). Old label: new.
#
# Plant: _next_n runs its first search whatever k is, so k == 0 is not inert.
# Witness: N0 on FRESH (the setter after it then poisons the iterator, so I from 0 answers PCREC_ERR_ITER), on BOUND (the continuation skips a match) and on ENDED.
# Reach (K35): reach tokens n0fresh, n0bound, n0ended; tests/findall/run_iter_diff.sh fails a run where it is 0.
SAB_ID="S1313-next-n-k0-runs-a-search"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='_next_n runs its first search whatever k is, so k == 0 is not inert'
SAB_DOC_FIGURE='Owed: lane i2build queued this row (docs/dev/lanes/i2build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1313.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    while (i < k && %s__one(it, capture_spans ? capture_spans + i * %s_NCAPS\n"'
SAB_AFTER='        "    while ((i < k || i == 0) && %s__one(it, capture_spans ? capture_spans + i * %s_NCAPS   /* SABOTAGE S1313 */\n"'
