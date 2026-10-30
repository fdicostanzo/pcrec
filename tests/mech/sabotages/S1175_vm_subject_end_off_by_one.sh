#!/usr/bin/env bash
# S1175 ([DD-11.5] P2d, lane ctxp2d) -- THE VM's `\z` FORM HOLDS ONE BYTE EARLY.
# VMCTX_END's test becomes `scan_position + 1 >= subject_length`, so a
# VM-routed `\z` also passes before the subject's last byte: `(a|ab)\z` on
# "aab" is (1,3) in libpcre2, (1,2) under the plant. The DFA is untouched, so only
# VM-routed `\z` cells (capture-bearing, or --engine=vm) can see it.
# RE-AIMED 2026-10-30 (lane vmrec, [VMREC] (a): the VM body as typed records):
# the \z test is now the BRANCH record's condition fragment; the same off-by-one. Same detector, same arm.
SAB_ID="S1175-vm-subject-end-off-by-one"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness assertions"
SAB_DESC='the VM'"'"'s \z test also passes at subject_length - 1'
SAB_DOC_FIGURE='OWED (lane ctxp2d): by hand 2026-10-20, harness over the 25 corpus files carrying \z 27 failed / 36087 passed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='        vm_frag_text(v->sb, &c, "scan_position == subject_length");'
SAB_AFTER='        vm_frag_text(v->sb, &c, "scan_position + 1 >= subject_length");   /* SABOTAGE S1175 */'
