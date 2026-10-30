# [VMREC] (a), lane vmrec, 2026-10-30: the record-first VM body's own rows
# (docs/dev/lanes/vmrec_report.md, "Structural checks and sabotages";
# design rev 3 mis-typing table, docs/dev/lanes/vmcons3_report.md).
#
# the one post-render rewrite closes the body; a record after it would be printed into text the respell already read, so vm_build refuses it (internal error) wherever a class table read is re-spelled.
SAB_ID="S1848-vm-record-after-respell"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="clspack harness"
SAB_HARNESS_TARGET="tests/base/clspack_atoms.rxt"
SAB_DESC='a checkpoint record is built after the class re-spelling closed the body'
SAB_DOC_FIGURE='lane vmrec 2026-10-30, probed by hand on a planted build: internal error on S403'\''s 12-atom witness --engine=vm (a checkpoint record built after the body was closed); scored by the owed vmrec-mech job'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    if (respell) vm_cls_respell(v);
}'
SAB_AFTER='    if (respell) { vm_cls_respell(v); vm_b_checkpoint(v->sb); }   /* SABOTAGE S1848 */
}'
