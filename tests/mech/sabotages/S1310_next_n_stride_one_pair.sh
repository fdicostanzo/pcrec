# S1310 -- [FINDALL-NEXT] I4 (lane i2build; docs/design/findall_iter_i2.md §5.4,
# docs/spec/match_api.md §3.8.1-§3.8.2). Old label: S1013.
#
# Plant: _next_n advances its entries by one pair, not NCAPS pairs, so a multi-group artifact's entries overlap.
# Witness: N2 on a VM group with NCAPS > 1 and >= 2 matches (`(a)` on `aaaa`), every group compared.
# Reach (K35): reach token vmcaps2 (VM cells with NCAPS > 1 and >= 2 matches); tests/findall/run_iter_diff.sh fails a run where it is 0.
SAB_ID="S1310-next-n-stride-one-pair"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='_next_n advances its entries by one pair, not NCAPS pairs, so the entries of a multi-group artifact overlap'
SAB_DOC_FIGURE='Owed: lane i2build queued this row (docs/dev/lanes/i2build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1310.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    while (i < k && %s__one(it, s, n, &lo%s, capture_spans + i * %s_NCAPS))\n"'
SAB_AFTER='        "    while (i < k && %s__one(it, s, n, &lo%s, capture_spans + i /* %s_NCAPS SABOTAGE S1310 */))\n"'
