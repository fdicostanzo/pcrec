# S1319 -- [FINDALL-NEXT] I4 (lane i2build; docs/design/findall_iter_i2.md §5.4,
# docs/spec/match_api.md §3.8.1-§3.8.2). Old label: new.
#
# Plant: _next_n clears the iterator's retry bit when it returns k, so an empty match that ends a batch is not retried by the next call.
# Witness: N1, N2, N3 on the retry groups (a*, x*|y, ...): spans against I.
# Reach (K35): reach token split (a call returned k with the retry bit set); tests/findall/run_iter_diff.sh fails a run where it is 0.
SAB_ID="S1319-next-n-drops-retry-at-k"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='_next_n clears the iterator retry bit when it returns k, so an empty match that ends a batch is not retried by the next call'
SAB_DOC_FIGURE='Owed: lane i2build queued this row (docs/dev/lanes/i2build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1319.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    return i;\n"'
SAB_AFTER='        "    if (i == k) it->flags &= ~PCREC_ITER_F_RETRY;   /* SABOTAGE S1319 */\n    return i;\n"'
