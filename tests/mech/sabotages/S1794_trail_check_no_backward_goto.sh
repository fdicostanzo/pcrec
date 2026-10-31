#!/usr/bin/env bash
# S1794 ([K134], lane trailgc2) -- NO CHECKPOINT ON A BACKWARD GOTO.
# vm_goto stops writing `<PREFIX>_TRAIL_CHECK()` before a jump that closes a
# trail-writing cycle, so a loop's trail growth never reaches the compaction
# (the run gives up where it answered). The emitted-C cycle check sees the
# uncovered cycle without running anything.
SAB_ID="S1794-trail-check-no-backward-goto"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="trailcompact"
SAB_DESC='vm_goto writes no trail checkpoint on a backward jump'
SAB_DOC_FIGURE='by hand 2026-10-29 (lane trailgc2): run_trail_compact.sh 17 failed / 17 passed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    if (vm_jump_closes_trail_cycle(v, id))'
SAB_AFTER='    if (0 && vm_jump_closes_trail_cycle(v, id))   /* SABOTAGE S1794 */'
