#!/usr/bin/env bash
# S1799 ([K134], lane trailgc3) -- A PARTIAL WALK FORGETS WHERE IT STARTS.
# When a compaction visits only the topmost `cap` frames, the trail below the
# lowest visited frame's segment is left as it is, so the read and write
# cursors start at that segment's start. The plant starts them at 0 while the
# frames below keep their marks: the segments under the walk merge into the
# first visited one and lose entries an unwind to those frames restores.
# Answers change at trail capacities below the live frame count.
SAB_ID="S1799-trail-compact-segment-start-ignored"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="trailcompact"
SAB_DESC='a partial compaction starts reading the trail at 0, not at its lowest segment'
SAB_DOC_FIGURE='by hand 2026-10-29 (lane trailgc3): run_trail_compact.sh 2 failed / 35 passed (partial-walk: 98 capture mismatches)'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='"    size_t r = f > 0 ? run->resume_stack[f - 1].trail_mark : 0, w = r;\n"'
SAB_AFTER='"    size_t r = 0, w = r;   /* SABOTAGE S1799 */\n"'
