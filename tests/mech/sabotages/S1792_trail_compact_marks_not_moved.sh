#!/usr/bin/env bash
# S1792 ([K134], lane trailgc2) -- THE FRAMES' TRAIL MARKS DO NOT MOVE.
# Compaction moves entries down; the plant leaves each live frame's
# trail_mark where it was, so an unwind rewinds to the wrong depth (and a
# call return reads its parked values at the wrong place).
SAB_ID="S1792-trail-compact-marks-not-moved"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="trailcompact"
SAB_DESC='the trail compaction leaves the live frames'"'"' trail marks unmoved'
SAB_DOC_FIGURE='by hand 2026-10-29 (lane trailgc2): run_trail_compact.sh 2 failed / 32 passed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='"        if (f > 0) run->resume_stack[f - 1].trail_mark = w;\n"'
SAB_AFTER='"        if (0 && f > 0) run->resume_stack[f - 1].trail_mark = w;   /* SABOTAGE S1792 */\n"'
