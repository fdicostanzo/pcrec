#!/usr/bin/env bash
# S1110 (lane b3b, [MEMFN] R17-b' B3b; Q-R17P-19 and the kit manager's Q-19:
# PCREC_NO_REQ_SET_LEAD stays a WORKING alias of `--memfn=no-pres-set-lead`)
# -- THE ALIAS DENIES THE WRONG ROW. The compile driver rewrites bit 45 into
# the kit's option string; the plant names `no-fd-pres-pick` instead, so the
# retired flag (and the library constant) is accepted, acts, and is not the
# deny it aliases. S462 is its sibling (the rewrite dropped: a silent no-op).
# Detector: the kit's presence check (run_presence.sh [alias], under
# memfnfinder): `-fno-req-set-lead`'s artifact must be the kit deny's.
SAB_ID="S1110-set-lead-alias-wrong-row"
SAB_FILE="src/core/compile.c"
SAB_SUITES="memfnfinder"
SAB_DESC="PCREC_NO_REQ_SET_LEAD (bit 45, retired) is rewritten to the wrong kit deny (no-fd-pres-pick), so the alias acts but is not --memfn=no-pres-set-lead"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        int w = snprintf(memfn_alias, sizeof memfn_alias, "%s%sno-pres-set-lead",'
SAB_AFTER='        int w = snprintf(memfn_alias, sizeof memfn_alias, "%s%sno-fd-pres-pick",   /* SABOTAGE S1110 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3b: see docs/dev/lanes/b3b_report.md (the solo mech run of this row)."
