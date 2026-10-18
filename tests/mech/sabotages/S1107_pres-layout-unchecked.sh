#!/usr/bin/env bash
# S1107 (lane b3b, [MEMFN] R17-b' B3b; r17b_prime.md rev 3 §1.6: "a site
# renders the table's pick") -- THE ROUTED DECISION IS NOT WHAT RENDERS. pcrec
# lays the pre-check's parts out from the kit's presence links and the define
# holds them to the links' layout (memfn/src/compose.c `pres_layout_check`);
# the plant accepts any parts, so a host that dropped a lead, a whole run or a
# rest member would render it silently. Detector: the kit's finder check
# (`pre-lead-run`, a lead dropped, must be refused naming the layout).
SAB_ID="S1107-pres-layout-unchecked"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the define no longer holds a pre-check's parts to its routed presence links' layout, so parts the kit did not decide render silently"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    mf_pres_picks pk;
    kit_pres_picks(art, s, &s->pres_proof, NULL, &pk);
    int run = -1, head = -1;'
SAB_AFTER='    return NULL;   /* SABOTAGE S1107 */
    mf_pres_picks pk;
    kit_pres_picks(art, s, &s->pres_proof, NULL, &pk);
    int run = -1, head = -1;'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3b: see docs/dev/lanes/b3b_report.md (the solo mech run of this row)."
