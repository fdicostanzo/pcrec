#!/usr/bin/env bash
# S919 ([MEMFN] R17-b' B1, lane fdb1; r17b_prime.md §8.3, §2.4; R-19) --
# `body` UNSTATED READ AS ONESHOT.
#
# WHAT IT BREAKS. `mf_site.body` (the call mode, knowledge key M) has an
# UNSTATED zero: a site that states no mode must DECLINE every finder row that
# reads M (R1, R2, R8), by the gate's rule 1. The plant makes the gate's
# classify of `body` (memfn/src/gate.c `cl_body`) read 0 as ONESHOT, so the
# rows' gate passes `body` on a site that never stated it.
#
# WHERE IT IS SEEN. No artifact moves. The finder check's call-mode gate
# (tests/memfn/finder_check.py I) runs a finder site with `body` 0 and one
# with ONESHOT under the traced kit: R1's gate record must name `body` (R1:
# UNSTATED) on the first and not on the second. Arm memfnfinder.
SAB_ID="S919-fd-body-unstated-read-as-oneshot"
SAB_FILE="memfn/src/gate.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the gate reads an UNSTATED call mode (mf_site.body 0) as ONESHOT, so the rows that read M pass their gate on a site that stated no mode"
SAB_DOC_FIGURE="HAND-MEASURED by lane fdb1: see docs/dev/lanes/fdb1_report.md (the solo mech run of this row)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    case MF_BODY_UNSTATED: return -1;'
SAB_AFTER='    case MF_BODY_UNSTATED: return CL_ONESHOT;   /* SABOTAGE S919 */'
