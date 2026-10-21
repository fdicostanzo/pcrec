# S1297 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: the VM accept label's NOTEMPTY_ATSTART guard is not emitted: the VM retry accepts the empty match it exists to reject.
# Detector: a vm-guard artifact's iterator repeats an empty match (DIFF against libpcre2) and its ITER_RETRY stamp no longer matches its text.
SAB_ID="S1297-vm-accept-guard-removed"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="findall"
SAB_DESC='the VM accept label'"'"'s NOTEMPTY_ATSTART guard is not emitted: the VM retry accepts the empty match it exists to reject'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1297.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            "    if (run->notempty && scan_position == ctx->pos) goto %s_fail;\n", v->p);'
SAB_AFTER='            "    (void)run->notempty; /* %s SABOTAGE S1297 */\n", v->p);'
