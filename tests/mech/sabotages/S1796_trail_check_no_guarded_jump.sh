#!/usr/bin/env bash
# S1796 ([K134], lane trailgc2) -- NO CHECKPOINT ON A CONDITIONAL BACK-JUMP.
# vm_jump (a site that writes its own `goto` inside a condition, such as the
# empty-iteration guard) drops the checkpoint from the jump it writes.
SAB_ID="S1796-trail-check-no-guarded-jump"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="trailcompact"
SAB_DESC='vm_jump writes a conditional backward jump without its trail checkpoint'
SAB_DOC_FIGURE='by hand 2026-10-29 (lane trailgc2): run_trail_compact.sh 2 failed / 32 passed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    return vm_rolef(v, "{ %s_TRAIL_CHECK(); goto %s_L%d; }", v->up, v->p, id);'
SAB_AFTER='    return vm_rolef(v, "{ (void)%s_trail_compact; (void)%s_trail_gc_at; goto %s_L%d; }", v->p, v->p, v->p, id);   /* SABOTAGE S1796 */'
