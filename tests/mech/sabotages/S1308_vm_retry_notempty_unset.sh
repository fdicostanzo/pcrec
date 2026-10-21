# S1308 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: the VM retry never arms the accept guard.
# Detector: every vm-guard retry cell repeats an empty match until the driver's cap.
SAB_ID="S1308-vm-retry-notempty-unset"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="findall"
SAB_DESC='the VM retry never arms the accept guard'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1308.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    run->notempty = 1;\n"'
SAB_AFTER='        "    /* SABOTAGE S1308 */\n"'
