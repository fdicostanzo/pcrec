#!/usr/bin/env bash
# S1089 ([MEMFN] R-23, lane r23; MF_SITE_ABI 14) -- AN UNSTATED `body` IS NOT
# REFUSED. `mf_site.body` (the call mode, knowledge key M) is a STATED fact
# with an UNSTATED zero: the kit's site check (`site_check`, read by mf_define
# and by the define-time query mf_ask) REFUSES a site that leaves it, so no
# builder inherits a mode by omission. The plant removes the refusal: an
# UNSTATED site then reaches the gate and the finder shadow, which only
# decline the rows that read M, and the compile goes on with no call mode.
#
# WHERE IT IS SEEN. No artifact moves (pcrec states `body` on every site).
# The finder check's call-mode family (tests/memfn/finder_check.py I) renders a
# site with `body` UNSTATED and demands the kit's refusal naming `body`; G2's
# refusal family carries the same case ("body-unstated"). Arm memfnfinder.
# S919, whose plant read an UNSTATED body as ONESHOT inside the gate, is
# superseded: nothing reaches the gate unstated any more.
SAB_ID="S1089-body-unstated-reaches-reader"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the kit's site check no longer refuses mf_site.body UNSTATED, so a site that states no call mode reaches the gate and the finder shadow instead of being refused"
SAB_DOC_FIGURE="HAND-MEASURED by lane r23: see docs/dev/lanes/r23_report.md (the solo mech run of this row)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (s->body == MF_BODY_UNSTATED)
        return "`body` UNSTATED (`body`: 0 is no call mode, MF_SITE_ABI 14)";'
SAB_AFTER='    if (0 && s->body == MF_BODY_UNSTATED)   /* SABOTAGE S1089 */
        return "`body` UNSTATED (`body`: 0 is no call mode, MF_SITE_ABI 14)";'
