# S1308 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: the VM retry runs the unguarded matcher.
# Detector: every retry cell of a retry-budgeted artifact repeats an empty match until the driver's cap.
SAB_ID="S1308-vm-retry-notempty-unset"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="findall"
SAB_DESC='the VM retry runs the unguarded matcher.'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1308.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    vm_emit_anchored_attempt(v, c, pcrec_sb_fragf(&v->cx->arena, "%s__match_notempty", v->p));'
SAB_AFTER='    vm_emit_anchored_attempt(v, c, pcrec_sb_fragf(&v->cx->arena, "%s_match_anchored", v->p));   /* SABOTAGE S1308 */'
