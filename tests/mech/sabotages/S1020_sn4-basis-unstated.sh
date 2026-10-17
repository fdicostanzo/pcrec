#!/usr/bin/env bash
# S1020 (SN-4; [MEMFN] R17-b' B1, lane fdb1; r17b_prime.md §8.3 [rev3 C2], §1.2)
# -- A FINDER ROW'S BASIS LEFT UNSTATED.
#
# WHAT IT BREAKS. Every finder row states its basis (MEASURED / DERIVED /
# UNMEASURED-DEFAULT), so a default is never read as measured: the listing
# and the facts section print it. The plant leaves R0's basis at the
# UNSTATED zero (memfn/src/finder.c `fd_rows[]`).
#
# WHERE IT IS SEEN. The table self-check (tests/memfn/finder_check.py A, arm
# memfnfinder) reads the kit's own listing (`mf_finder_rows`) and fails a row
# whose basis is not one of the three.
SAB_ID="S1020-sn4-basis-unstated"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the finder row R0 states no basis (FB_UNSTATED), so its listing reads no provenance for a set-reading decision"
SAB_DOC_FIGURE="HAND-MEASURED by lane fdb1: see docs/dev/lanes/fdb1_report.md (the solo mech run of this row)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      FF_WALK, FF_UNSTATED, { 0, 0, 0, 0 }, 0, "fd-r0", FB_DERIVED, "B4",'
SAB_AFTER='      FF_WALK, FF_UNSTATED, { 0, 0, 0, 0 }, 0, "fd-r0", FB_UNSTATED, "B4",   /* SABOTAGE S1020 */'
