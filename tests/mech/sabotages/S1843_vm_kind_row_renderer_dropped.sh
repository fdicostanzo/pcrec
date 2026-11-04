# [VMREC] (a), lane vmrec, 2026-10-30: the record-first VM body's own rows
# (docs/dev/lanes/vmrec_report.md, "Structural checks and sabotages";
# design rev 3 mis-typing table, docs/dev/lanes/vmcons3_report.md).
#
# a kind without a renderer: vm_build refuses the record (internal error) rather than printing nothing, on every VM compile that builds a goto.
SAB_ID="S1843-vm-kind-row-renderer-dropped"
SAB_FILE="src/gen/vm_stmt.c"
SAB_SUITES="codegen"
SAB_DESC='the goto kind'\''s row in vm_kind_rows[] loses its renderer, so a goto record has nothing to print it'
SAB_DOC_FIGURE='lane vmrec 2026-10-30, probed by hand on a planted build: internal error on a(b|c)+d --engine=vm (record kind 2 has no renderer); scored by the owed vmrec-mech job'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    [VK_GOTO]         = { VK_GOTO,         "goto",         vm_r_goto },'
SAB_AFTER='    [VK_GOTO]         = { VK_GOTO,         "goto",         0 ? vm_r_goto : NULL },   /* SABOTAGE S1843 */'
