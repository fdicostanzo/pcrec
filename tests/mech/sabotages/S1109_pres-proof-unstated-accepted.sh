#!/usr/bin/env bash
# S1109 (lane b3b, [MEMFN] R17-b' B3b; memfn.h MF_SITE_ABI 17, `pres_proof`)
# -- AN UNSTATED PROOF READ AS A FACT. A site stating presence spans must state
# the start search's proof (P2 reads it); its zero is UNSTATED and refused,
# never read as "byte 0 proven" (pcrec-no-silent-defaults). The plant accepts
# it. pcrec always states the proof, so no artifact moves: the detector is the
# kit's contract check (finder_check M: `pre-noproof` refused naming
# pres_proof).
SAB_ID="S1109-pres-proof-unstated-accepted"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC="a site stating presence spans may leave pres_proof UNSTATED, which P2 then reads as a stated fact (byte 0, no stop, no run)"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (s->npspan && pf->stated != 1)'
SAB_AFTER='    if (0 && s->npspan && pf->stated != 1)   /* SABOTAGE S1109 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3b: see docs/dev/lanes/b3b_report.md (the solo mech run of this row)."
