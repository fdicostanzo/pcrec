#!/usr/bin/env bash
# SKB2-1 (SN-1's shape; placeholder id, main allocates) -- D1's ROUTED BIT
# LEFT 0 after B2: one-byte sites render their pre-table form, which is the
# same text (zero movers), so byte identity cannot see it (§1.6 [rev3 B5]).
# Detectors (memfnfinder): A (D1 routed 1 at B2) and K (byte1t decided by D1;
# the routed record), and the routed census's D1 floors.
SAB_ID="SKB2-1-fd-d1-unrouted"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC="finder row D1 keeps routed 0 after its routing step: its sites render their pre-table form under no routed decision"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      FF_LIBC, FF_UNSTATED, { 0, 0, 0, 0 }, 1, "fd-d1", FB_UNMEASURED_DEFAULT, "B2",'
SAB_AFTER='      FF_LIBC, FF_UNSTATED, { 0, 0, 0, 0 }, 0, "fd-d1", FB_UNMEASURED_DEFAULT, "B2",   /* SABOTAGE SKB2-1 */'
