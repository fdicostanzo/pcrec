# [VMREC] (a), lane vmrec, 2026-10-30: the record-first VM body's own rows
# (docs/dev/lanes/vmrec_report.md, "Structural checks and sabotages";
# design rev 3 mis-typing table, docs/dev/lanes/vmcons3_report.md).
#
# M12's comment-tier twin: under the default -fno-comments the text is dropped, so the artifact's BYTES do not move; the tiling clock is the UNCUT length (dropped comment bytes included), so it still fails, and the static scan does not depend on the tier at all.
SAB_ID="S1841-vm-raw-comment-tier-print"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="stmtwriter codegen"
SAB_DESC='emit_vm.c writes a non-essential comment line straight into the VM body buffer after each label record; a default compile drops its text'
SAB_DOC_FIGURE='lane vmrec 2026-10-30, probed by hand on a planted build: internal error on a(b|c)+d --engine=vm (48 bytes where 32: the dropped comment counts in the uncut clock); the scan names emit_vm.c; scored by the owed vmrec-mech job'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    vm_b_label(v->sb, id, role);
    vm_ev(v, VE_LABEL, id, 0, role);'
SAB_AFTER='    vm_b_label(v->sb, id, role);
    pcrec_sb_cmt_open(&v->cx->job->vmsb, PCREC_CMT_NONESSENTIAL);   /* SABOTAGE S1841 */
    pcrec_sb_puts(&v->cx->job->vmsb, "    /* S1841 */\n");
    pcrec_sb_cmt_close(&v->cx->job->vmsb);
    vm_ev(v, VE_LABEL, id, 0, role);'
