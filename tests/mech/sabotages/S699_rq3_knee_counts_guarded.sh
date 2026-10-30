#!/usr/bin/env bash
# S699 ([MEMFN] RQ-3, lane rq3, 2026-10-09) -- the VM entry-shape knee drops
# the guarded subtraction: `program_bytes` reads `pcrec_sb_len_uncut` again,
# so a SIMD-on program would move the rung and `<PREFIX>_VM_PROGRAM_BYTES`.
# Invisible on the plain build (nothing is guarded); the witness build's VM
# block is counted, so every VM artifact's VM_PROGRAM_BYTES (and every
# knee-near rung) differs from the plain build's.
# RE-AIMED 2026-10-30 (lane vmrec, [VMREC] (a): the VM body as typed records):
# the knee's and VM_PROGRAM_BYTES' one read of the body length is vm_stmt_program_bytes; the same uncut read there. Same detector, same arm.
SAB_ID='S699-rq3-knee-counts-guarded'
SAB_FILE="src/gen/vm_stmt.c"
SAB_SUITES='simdguarded'
SAB_DESC="the entry-shape knee and VM_PROGRAM_BYTES read the uncut length again, guarded bytes included"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S699. docs/dev/lanes/rq3_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return pcrec_sb_len_decide(sb->b);'
SAB_AFTER='    return pcrec_sb_len_uncut(sb->b);   /* SABOTAGE S699 */'
