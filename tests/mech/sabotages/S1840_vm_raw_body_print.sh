# [VMREC] (a), lane vmrec, 2026-10-30: the record-first VM body's own rows
# (docs/dev/lanes/vmrec_report.md, "Structural checks and sabotages";
# design rev 3 mis-typing table, docs/dev/lanes/vmcons3_report.md).
#
# M12, a raw print into the body. Two nets: the tiling check fails every VM compile at the next record (codegen), and the static scan names the buffer outside vm_stmt.c (stmtwriter).
SAB_ID="S1840-vm-raw-body-print"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="stmtwriter codegen"
SAB_DESC='emit_vm.c writes one raw byte into the VM body buffer after each label record, outside every renderer'
SAB_DOC_FIGURE='lane vmrec 2026-10-30, probed by hand on a planted build: internal error on a(b|c)+d --engine=vm (body 33 bytes where the label record left 32); the scan names emit_vm.c; scored by the owed vmrec-mech job'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    vm_b_label(v->sb, id, role);
    vm_ev(v, VE_LABEL, id, 0, role);'
SAB_AFTER='    vm_b_label(v->sb, id, role);
    pcrec_sb_puts(&v->cx->job->vmsb, ";");   /* SABOTAGE S1840 */
    vm_ev(v, VE_LABEL, id, 0, role);'
