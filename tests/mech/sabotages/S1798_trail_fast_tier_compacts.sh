#!/usr/bin/env bash
# S1798 ([K134], lane trailgc3) -- THE FAST TIER COMPACTS.
# The fast tier's FRAMES give-up escalates to a deep tier that re-runs the
# match, so its floor is never (review 2026-10-29-r2 F5). The plant drops
# that override: the fast tier compacts at the bind's floor, spends work
# before the same escalation (+15-24% instructions) or, on a subject whose
# live trail fits it, answers without escalating, which the witnesses'
# exactly-one-escalation check reads.
SAB_ID="S1798-trail-fast-tier-compacts"
SAB_FILE="src/gen/emit_comb.c"
SAB_SUITES="trailcompact"
SAB_DESC='the fast tier keeps the bind'"'"'s trail compaction floor instead of never'
SAB_DOC_FIGURE='by hand 2026-10-29 (lane trailgc3): see the lane report'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='        if (fast_no_compact)'
SAB_AFTER='        if (0 && fast_no_compact)   /* SABOTAGE S1798 */'
