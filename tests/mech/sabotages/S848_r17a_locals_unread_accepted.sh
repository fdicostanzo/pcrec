#!/usr/bin/env bash
# S848 ([MEMFN] R17-a, lane r17a; setfind.md rev 2.3 §12.5, r4 K1-8) -- THE
# "PLACED, NEVER READ" REFUSAL REMOVED.
#
# WHAT IT BREAKS. mf_art_end refuses a decl_point site whose mf_locals came
# but no use followed it (memfn.h): storage placed and never read is an
# unused variable under the harness's -Werror, and the protocol's own record
# of a storage point with no use. The plant disables that test, so such a
# site falls through to the generic "defined, never used" refusal, which
# names no field and says nothing of the storage.
#
# WHERE IT IS SEEN. No artifact moves. C5's gate case locals-unread (define,
# mf_locals, end) is still refused, but by the generic text, which does not
# name `decl_point` (run_arm_pins.sh check 6 reads the field). Arm
# memfnarms. (At R17-b test-codegen's -Wunused-variable on a planted
# artifact is the second line.)
SAB_ID="S848-r17a-locals-unread-accepted"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnarms"
SAB_DESC="mf_art_end no longer refuses a decl_point site whose storage was placed and never read (the refusal falls to the generic never-used text)"
SAB_DOC_FIGURE="HAND-MEASURED by lane r17a: see docs/dev/lanes/r17a_report.md (the solo mech run of this row)."
SAB_REACH='$CC -std=gnu11 -I"$TREE/memfn/include" "$TREE/tests/memfn/arm_fixtures.c" "$TREE/build/libpcrec.a" -o fx && ./fx --gate'
SAB_REACH_EXPECT='locals-unread	REFUSE	mf_art_end: handle 1'"'"'s storage placed, never read (`decl_point`: an mf_locals no use followed)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (r->placed && !r->used)'
SAB_AFTER='        if (0 && r->placed && !r->used)     /* SABOTAGE S848 */'
