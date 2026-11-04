#!/usr/bin/env bash
# S1796 ([K134], lane trailgc2) -- NO CHECKPOINT ON A CONDITIONAL BACK-JUMP.
# vm_jump (a site that writes its own `goto` inside a condition, such as the
# empty-iteration guard) drops the checkpoint from the jump it writes.
# RE-AIMED 2026-10-30 (lane vmrec, [VMREC] (a): the VM body as typed records):
# a guarded jump's checkpoint block is now the target renderer's (vm_tgt_render), the checkpoint still counted by vm_jump_tgt; the same block written without the check. Same detector, same arm.
SAB_ID="S1796-trail-check-no-guarded-jump"
SAB_FILE="src/gen/vm_stmt.c"
SAB_SUITES="trailcompact"
SAB_DESC='vm_jump writes a conditional backward jump without its trail checkpoint'
SAB_DOC_FIGURE='by hand 2026-10-29 (lane trailgc2): run_trail_compact.sh 2 failed / 32 passed; re-anchored by lane trailgc3 (one checkpoint writer, F9: the plant still counts the site, writes no check), intent unchanged: 2 failed / 36 passed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            pcrec_sb_printf(sb->b, "{ %s_TRAIL_CHECK(); goto %s_L%d; }",
                            sb->up, sb->p, t->lbl);'
SAB_AFTER='            pcrec_sb_printf(sb->b, "{ (void)%s_trail_compact; (void)%s_trail_gc_at; goto %s_L%d; }",
                            sb->p, sb->p, sb->p, t->lbl);   /* SABOTAGE S1796 */'
