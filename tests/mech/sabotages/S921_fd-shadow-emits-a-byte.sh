#!/usr/bin/env bash
# S921 ([MEMFN] R17-b' B1, lane fdb1; r17b_prime.md §8.3, §1.6) -- THE SHADOW
# CALL EMITS A BYTE.
#
# WHAT IT BREAKS. B1's finder table decides nothing that renders: its shadow
# writes trace records only, and the define that hosts it writes exactly the
# chosen row's text (zero artifact movers is B1's whole claim). The plant
# writes one comment into the define's file-scope sink beside the shadow's
# call (memfn/src/compose.c `define_sel`), in EVERY build, so every defined
# site's artifact gains bytes.
#
# WHERE IT IS SEEN. C5's pinned fixture renderings (tests/memfn/run_arm_pins.sh,
# arm memfnarms): every fixture's `def` part digest moves. (The design names
# emit_sweep's sample as this row's detector; the pins see the same byte with
# no reference build.)
# B4' (lane b4p) retired the shadow itself; the plant stands as the control
# that the define hosting the finder's decision writes no byte of its own.
SAB_ID="S921-fd-shadow-emits-a-byte"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnarms"
SAB_DESC="the define that hosts the finder shadow writes a byte of its own into the file scope, so every defined site's artifact moves"
SAB_DOC_FIGURE="HAND-MEASURED by lane fdb1: see docs/dev/lanes/fdb1_report.md (the solo mech run of this row)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (row->define(art, h, def, file_scope)) return -1;'
SAB_AFTER='    if (file_scope && file_scope->puts) file_scope->puts(file_scope->u, "/*fd*/\n");   /* SABOTAGE S921 */
    if (row->define(art, h, def, file_scope)) return -1;'
