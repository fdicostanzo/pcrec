#!/usr/bin/env bash
# S619 ([MEMFN] M4 prep, lane m4) -- A ROW SERVES A LOOP-EXIT on_miss INSIDE
# ITS OWN LOOP.
#
# WHAT IT BREAKS. RULED Q-R7-3 (MF_SITE_ABI 6): `on_miss` `break;` is its own
# class, LOOP_EXIT. It leaves pcrec's loop, so a row may paste it only where
# its text opens no loop of its own around it; the generic row, whose loops
# are its own business and never a promise, does not serve it, and a
# LOOP_EXIT site no other row serves is REFUSED naming `on_miss`. The plant
# makes the generic row serve LOOP_EXIT, so such a site renders through a
# row that may wrap it in its own loop, where `break;` would leave the kit's
# loop instead of pcrec's.
#
# WHERE IT IS SEEN. pcrec's one LOOP_EXIT site (MLINE) is served by
# pf_memchr_back first, so no artifact moves. The gate cases
# `back-excluded-break-refused` and `pf-memchr-break-refused` (a LOOP_EXIT
# site the back row declines; an offset-0 memchr site, whose row serves
# JUMP/BRACED only) must be REFUSED naming `on_miss`; with the plant they
# RENDER through generic. Arm memfnarms (run_arm_pins.sh check 6).
SAB_ID="S619-m4-loop-exit-inside-row-loop"
SAB_FILE="memfn/src/generic.c"
SAB_SUITES="memfnarms"
SAB_DESC="the generic row serves the LOOP_EXIT on_miss class (Q-R7-3), so a 'break;' site no no-loop row serves renders through a row whose text may enclose it in its own loop instead of being refused naming on_miss"
SAB_DOC_FIGURE="HAND-MEASURED by lane m4 (plant applied, tree rebuilt): run_arm_pins.sh check 6, two gate cases RENDER generic instead of REFUSE on_miss; see docs/dev/lanes/m4_report.md §6. The matrix's own figure is owed at the slot."
SAB_REACH='$CC -std=gnu11 -I"$TREE/memfn/include" "$TREE/tests/memfn/arm_fixtures.c" "$TREE/build/libpcrec.a" -o fx && ./fx --gate'
SAB_REACH_EXPECT='back-excluded-break-refused	REFUSE	mf_use: row `generic` does not serve this use of handle 1: `on_miss` (R2: stated as LOOP_EXIT, not served)
pf-memchr-break-refused	REFUSE'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    [FLD_on_miss]         = MF_ANY & ~CM(LOOP_EXIT),'
SAB_AFTER='    [FLD_on_miss]         = MF_ANY,  /* SABOTAGE S619: generic serves LOOP_EXIT */'
