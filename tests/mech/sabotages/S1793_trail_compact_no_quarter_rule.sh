#!/usr/bin/env bash
# S1793 ([K134], lane trailgc2) -- THE QUARTER RULE IS GONE.
# A compaction that leaves less than a quarter of the trail free below the
# floor stops compacting for the attempt; the plant always re-arms at the
# floor, so a nearly-full trail compacts at every checkpoint (unbounded work
# per trail write). No answer changes; the boundary moves from 4n + 17 to
# 3n + 13 for the specimen, which run_trail_compact.sh §4 pins.
SAB_ID="S1793-trail-compact-no-quarter-rule"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="trailcompact"
SAB_DESC='the trail compaction re-arms at the floor however little room it made'
SAB_DOC_FIGURE='by hand 2026-10-29 (lane trailgc2): run_trail_compact.sh 2 failed / 32 passed; re-anchored by lane trailgc3 (the floor is the run state'"'"'s since F5), intent unchanged: 1 failed / 37 passed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='"    return w + cap / 4 <= run->trail_gc_floor ? run->trail_gc_floor : (size_t)-1;\n"'
SAB_AFTER='"    return run->trail_gc_floor;   /* SABOTAGE S1793 */\n"'
