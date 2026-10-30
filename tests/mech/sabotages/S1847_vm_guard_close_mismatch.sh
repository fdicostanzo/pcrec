# [VMREC] (a), lane vmrec, 2026-10-30: the record-first VM body's own rows
# (docs/dev/lanes/vmrec_report.md, "Structural checks and sabotages";
# design rev 3 mis-typing table, docs/dev/lanes/vmcons3_report.md).
#
# a GUARD and its GUARD_END in different spellings: the guard stack refuses the close (internal error) on every revdet walk that captures.
SAB_ID="S1847-vm-guard-close-mismatch"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/rungselect/rungselect.rxt"
SAB_DESC='the revdet capture walk closes an inline-braced GUARD with a braced close'
SAB_DOC_FIGURE='lane vmrec 2026-10-30, probed by hand on a planted build: internal error on ((a)|b){0,4}c and ((a)|b)*c --engine=vm (a guard'\''s close does not match its guard); scored by the owed vmrec-mech job'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            vm_b_guard_end(v->sb, VG_INLINE_BRACED);'
SAB_AFTER='            vm_b_guard_end(v->sb, VG_BRACED);   /* SABOTAGE S1847 */'
