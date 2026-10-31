# [VMREC] (a), lane vmrec, 2026-10-30: the record-first VM body's own rows
# (docs/dev/lanes/vmrec_report.md, "Structural checks and sabotages";
# design rev 3 mis-typing table, docs/dev/lanes/vmcons3_report.md).
#
# M14, a renderer printing a target its record does not hold: the program jumps somewhere else, so VM answers move (RT, the independent reader, is not built in (a); the corpus is the net).
SAB_ID="S1845-vm-branch-wrong-target"
SAB_FILE="src/gen/vm_stmt.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/backrefs"
SAB_DESC='a BRANCH record renders its condition'\''s jump to the FAIL label instead of the label it holds, on the branches that carry no trail checkpoint (a target that exists and is wrong; the first spelling, label+1, named a label that does not exist and did not compile)'
SAB_DOC_FIGURE='lane vmrec 2026-10-30, probed by hand on a planted build: tests/backrefs/nested.rxt: 28 cases failed, 8 passed; scored by the owed vmrec-mech job'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    vm_tgt_render(sb, &s->u.branch.t);
    pcrec_sb_puts(sb->b, "\n");'
SAB_AFTER='    VmTgt t_ = s->u.branch.t;   /* SABOTAGE S1845 */
    if (t_.k == VT_LABEL && !t_.ckpt) t_ = pcrec_vm_tgt_fail();
    vm_tgt_render(sb, &t_);
    pcrec_sb_puts(sb->b, "\n");'
