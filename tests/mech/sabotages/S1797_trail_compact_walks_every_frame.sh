#!/usr/bin/env bash
# S1797 ([K134], lane trailgc3) -- THE COMPACTION WALKS EVERY LIVE FRAME.
# A compaction visits the segments of at most `cap` live frames, the
# topmost, so its work is bounded by the trail writes that pay for it
# (review 2026-10-29-r2 F1). The plant starts the walk at frame 0, so with
# frames >> trail every compaction walks them all: answers stay right, but
# the bounded-work witness (a million frames, a 64-entry trail) runs for
# seconds instead of milliseconds.
SAB_ID="S1797-trail-compact-walks-every-frame"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="trailcompact"
SAB_DESC='the trail compaction walks every live frame instead of the topmost cap'
SAB_DOC_FIGURE='by hand 2026-10-29 (lane trailgc3): see the lane report'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='"    size_t f = top > cap ? top - cap : 0, k;\n"'
SAB_AFTER='"    size_t f = 0, k;   /* SABOTAGE S1797 */\n"'
