#!/usr/bin/env bash
# S1791 ([K134], lane trailgc2) -- THE SEEN MAP LEAKS ACROSS SEGMENTS.
# The per-slot "seen" map is cleared after each segment; the plant never
# clears it, so a slot written in an older segment loses its entry in every
# newer one, and an unwind to that newer frame no longer restores it.
SAB_ID="S1791-trail-compact-seen-not-cleared"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="trailcompact"
SAB_DESC='the trail compaction never clears its per-segment seen map'
SAB_DOC_FIGURE='by hand 2026-10-29 (lane trailgc2): run_trail_compact.sh 3 failed / 28 passed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='"        for (k = kept; k < w; k++) seen[run->trail[k].slot_index] = 0;\n"'
SAB_AFTER='"        for (k = kept; k < kept; k++) seen[run->trail[k].slot_index] = 0;   /* SABOTAGE S1791 */\n"'
