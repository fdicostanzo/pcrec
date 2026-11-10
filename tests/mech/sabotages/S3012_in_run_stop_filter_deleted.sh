#!/usr/bin/env bash
# S3012 -- R-38 K38-2a, review 2026-11-10 r2 k382a FAM-5 (lane k382afix; docs/design/memfn/
# span_runs_sheet.md rev 1.3 §5's K38-2a row, kit ruling [r1.3 K7]). THE IN-RUN STOP IS NO
# LONGER THE RUN DECISION'S: a_mass_choose (window.c) loses its in-run filter (the `continue`
# that leaves R's positions to kit_run_decide's one stop), so inside a verify-YES run the stop is
# picked by T_MASS_STRETCH directly again and the run-tie-left lever no longer moves it.
# tests/memfn/decider_census.py D stays green on this plant (it counts the kit_run_decide CALL,
# which stays; its header states the limit).
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh): in the run-tie-left pass the
# window's stop and the run decision disagree, mf_define refuses the layout ("its run part is
# not the WINDOW its presence link verifies"), and the generator's failures red the pass.
SAB_ID="S3012-in-run-stop-filter-deleted"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2pres"
SAB_DESC="a_mass_choose's in-run filter deleted: the in-run stop reads T_MASS_STRETCH directly, G2's lever pass must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382afix 2026-11-10 (docs/dev/lanes/k382afix_report.md): memfn/tests/run_g2_pres.sh --plant S3012 RED (the lever pass's generator: mf_define refuses the layout). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3012."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (r && p->stretch && o >= r->start && o < r->start + r->len && o != rs)
            continue;                   /* inside R: the run decision'"'"'s one */'
SAB_AFTER='        (void)o; (void)rs;   /* SABOTAGE S3012 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
