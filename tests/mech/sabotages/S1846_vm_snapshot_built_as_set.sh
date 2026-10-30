# [VMREC] (a), lane vmrec, 2026-10-30: the record-first VM body's own rows
# (docs/dev/lanes/vmrec_report.md, "Structural checks and sabotages";
# design rev 3 mis-typing table, docs/dev/lanes/vmcons3_report.md).
#
# M7 (r8 SOUND-7): SET refuses a self-copy source, so the mis-typed record is an internal error on every compile with a parking call site.
SAB_ID="S1846-vm-snapshot-built-as-set"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC='a call site'\''s park of a slot'\''s own value is built as a SET whose source is the slot itself'
SAB_DOC_FIGURE='lane vmrec 2026-10-30, probed by hand on a planted build: internal error on ^(a|b(?1))$ --engine=vm and on C6'\''s ^(x(?>a(?1)?b)y)$ -fno-splice-calls (a SET of slot 2 copies the slot onto itself); scored by the owed vmrec-mech job'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    vm_b_snapshot(v->sb, slot, vm_slot_name(v, slot));'
SAB_AFTER='    vm_b_set(v->sb, slot, vm_slot_name(v, slot),   /* SABOTAGE S1846 */
             vm_slot_name(v, slot)
             ? vm_rolef(v, "slot_values[%s_%s]", v->up, vm_slot_name(v, slot))
             : vm_rolef(v, "slot_values[%d]", slot));'
