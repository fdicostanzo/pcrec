#!/usr/bin/env bash
# S1107 (lane b3b, [MEMFN] R17-b' B3b; r17b_prime.md rev 3 §1.6: "a site
# renders the table's pick") -- THE ROUTED DECISION IS NOT WHAT RENDERS. pcrec
# lays the pre-check's parts out from the kit's presence links and the define
# holds them to the links' layout (memfn/src/compose.c `pres_layout_check`);
# the plant accepts any parts, so a host that dropped a lead, a whole run or a
# rest member would render it silently. Detector: the kit's finder check
# (`pre-lead-run`, a lead dropped, must be refused naming the layout).
# RE-AIMED 2026-11-11 (lane k382, R-38 K38-2): pres_layout_check's RUN half is a statement rule now (a FUNC part
# where the run's tested link orders it; the kit derives the part, so it can no longer
# disagree with a pick), so the row's intent is the HEAD and REST halves: the same plant
# (skip the whole check) at the rewritten function's top. Detector unchanged: finder_check's
# pre-lead-run (P4 leads, the head part dropped) must be refused naming the layout. The run
# decision's own disagreement is the per-reader tie plant's (S1095).
SAB_ID="S1107-pres-layout-unchecked"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC='the define no longer holds a pre-check'"'"'s parts to its routed presence links'"'"' layout (the head and rest halves; the run half is a statement rule), so a dropped lead or rest member renders silently'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    (void)art;
    int run = kit_pres_run(s), head = -1;'
SAB_AFTER='    return NULL;   /* SABOTAGE S1107 */
    (void)art;
    int run = kit_pres_run(s), head = -1;'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3b: see docs/dev/lanes/b3b_report.md (the solo mech run of this row)."
