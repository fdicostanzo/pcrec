# S1297 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: the guarded matcher's NOTEMPTY_ATSTART line never rejects: the VM retry accepts the empty match it exists to reject.
# Detector: a retry-budgeted artifact's iterator repeats an empty match (DIFF against libpcre2).
SAB_ID="S1297-vm-accept-guard-removed"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="findall"
SAB_DESC='the guarded matcher'"'"'s NOTEMPTY_ATSTART line never rejects: the VM retry accepts the empty match it exists to reject.'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1297.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    if (scan_position == ctx->pos) goto %s_fail;\n"'
SAB_AFTER='        "    if (0) goto %s_fail; /* SABOTAGE S1297 */\n"'
