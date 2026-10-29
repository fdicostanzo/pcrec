#!/usr/bin/env bash
# S1795 ([K134], lane trailgc2) -- NO CHECKPOINT ON A REGION RETURN.
# A chain of returns writes the callers' restores once per level and passes
# no backward goto; the plant drops the return's own checkpoint, so deep
# recursion's unwinding growth never reaches the compaction.
SAB_ID="S1795-trail-check-no-return"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="trailcompact"
SAB_DESC='a region return writes no trail checkpoint'
SAB_DOC_FIGURE='by hand 2026-10-29 (lane trailgc2): run_trail_compact.sh 4 failed / 30 passed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    vm_trail_check(v);
    /* THE SECOND INDIRECT JUMP'
SAB_AFTER='    /* SABOTAGE S1795 */
    /* THE SECOND INDIRECT JUMP'
