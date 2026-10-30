# [VMREC] (a), lane vmrec, 2026-10-30: the record-first VM body's own rows
# (docs/dev/lanes/vmrec_report.md, "Structural checks and sabotages";
# design rev 3 mis-typing table, docs/dev/lanes/vmcons3_report.md).
#
# the kind table naming the wrong renderer: every renderer checks the record's kind (vm_renders), so the swap is an internal error, not a wrong program.
SAB_ID="S1844-vm-renderers-swapped"
SAB_FILE="src/gen/vm_stmt.c"
SAB_SUITES="codegen"
SAB_DESC='the goto and fail rows of vm_kind_rows[] name each other'\''s renderer'
SAB_DOC_FIGURE='lane vmrec 2026-10-30, probed by hand on a planted build: internal error on a(b|c)+d --engine=vm (the goto renderer handed a fail record); scored by the owed vmrec-mech job'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    [VK_GOTO]         = { VK_GOTO,         "goto",         vm_r_goto },
    [VK_FAIL]         = { VK_FAIL,         "fail",         vm_r_fail },'
SAB_AFTER='    [VK_GOTO]         = { VK_GOTO,         "goto",         vm_r_fail },   /* SABOTAGE S1844 */
    [VK_FAIL]         = { VK_FAIL,         "fail",         vm_r_goto },'
