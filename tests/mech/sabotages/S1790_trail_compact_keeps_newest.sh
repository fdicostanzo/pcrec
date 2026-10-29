#!/usr/bin/env bash
# S1790 ([K134], lane trailgc2) -- THE TRAIL COMPACTION KEEPS THE WRONG ENTRY.
# Within a segment between two live frames only a slot's OLDEST entry is ever
# restored; the plant drops the oldest and keeps every later one, so an
# unwind across a compacted segment restores a value the slot never had at
# the frame's push. Answers change at small trail capacities.
SAB_ID="S1790-trail-compact-keeps-newest"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="trailcompact"
SAB_DESC='the trail compaction drops a slot'"'"'s oldest entry per segment and keeps the later ones'
SAB_DOC_FIGURE='by hand 2026-10-29 (lane trailgc2): run_trail_compact.sh 6 failed / 24 passed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='"            if (seen[s]) continue;\n"'
SAB_AFTER='"            if (!seen[s]) { seen[s] = 1; continue; }   /* SABOTAGE S1790 */\n"'
