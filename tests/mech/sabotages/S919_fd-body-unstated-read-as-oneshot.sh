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
# RETIRED 2026-10-17 (lane r23, R-23, MF_SITE_ABI 14): `body` is a STATED fact
# and the kit's site check REFUSES an UNSTATED one before any selection, so
# the gate never sees the state this plant misreads: the row's population is
# gone and it is DECLARED UNREACHED. Its successor is S1089 (the refusal). The
# REACH_POP below asks for the finder check's old line naming the gate's
# `body` UNSTATED decline: the day a path delivers an unstated body to the
# gate again, this row reads NOW REACHED and must be re-aimed.
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
SAB_REACH_POP='tests/memfn/finder_check.py|"body:R1:UNSTATED" in ln|1'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='the kit refuses a site whose body is UNSTATED (R-23, site_check) before the gate reads it, so the plant misclassifies a state no site reaches; the REACH_POP reads NOW REACHED if the finder check delivers an unstated body to the gate again'
SAB_COUNT=1
SAB_BEFORE='    case MF_BODY_UNSTATED: return -1;'
SAB_AFTER='    case MF_BODY_UNSTATED: return CL_ONESHOT;   /* SABOTAGE S919 */'
