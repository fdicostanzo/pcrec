#!/usr/bin/env bash
# S3012 -- R-38 K38-2a, review 2026-11-10 r2 k382a FAM-5 (lane k382afix; docs/design/memfn/
# span_runs_sheet.md rev 1.3 §5's K38-2a row, kit ruling [r1.3 K7]). THE IN-RUN STOP IS NO
# LONGER THE RUN DECISION'S: a_mass_choose (window.c) loses its in-run filter (the `continue`
# that leaves R's positions to kit_run_decide's one stop), so inside a verify-YES run the stop is
# picked by T_MASS_STRETCH directly again and the run-tie-left lever no longer moves it.
# tests/memfn/decider_census.py D stays green on this plant (it counts the kit_run_decide CALL,
# which stays; its header states the limit).
# RE-AIMED 2026-11-14 (lane mechund): since [RUN-POS-SET] stage 3 the derived run part is a direct
# translation of the reply (part_d.md §2.1), so g2pres no longer reaches the filter; the detector is G2's WINDOW family
# (memfn/tests/run_g2_win.sh, arm g2win): its in-run sites' DECIDE check reds (86 fails on the plant, 2026-11-14).
# RUNNER TWIN (lane s3012fix, 2026-11-24): run_g2_win.sh's own S3012, the same edit and detector
# (PLANT_TWINS; its --plant asserts an in-run DECIDE FAIL). It sat in run_g2_pres.sh until then.
# Former detector: G2's presence family (memfn/tests/run_g2_pres.sh): in the run-tie-left pass the
# window's stop and the run decision disagree, mf_define refuses the layout ("its run part is
# not the WINDOW its presence link verifies"), and the generator's failures red the pass.
SAB_ID="S3012-in-run-stop-filter-deleted"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2win"
SAB_DESC="a_mass_choose's in-run filter deleted: the in-run stop reads T_MASS_STRETCH directly, G2's window family must red"
SAB_DOC_FIGURE="G2's WINDOW family (memfn/tests/run_g2_win.sh, arm g2win): 86 fails on the plant (lane mechund 2026-11-14). The reach is MEASURED and gated on the filter-decisive population (lane fixposts2b 2026-11-15, review r3 CHECKS-1; same generator, seed 20261022, a hand-built plant lib): clean prints REACH-G2W-INRUN rendered=200 decisive=43 agree=200. The matrix runs the probe on the CLEAN tree only, so the token is a clean-tree reach argument, not a plant detector: decisive comes from the reference alone (plant-independent) and is at or above its floor, and the library agrees at every in-run site, so the library carries the filter's effect where it decides. Plant-sensitivity EVIDENCE (by hand, not exercised by the matrix): the planted build reads rendered=200 decisive=43 agree=157 (review r4 fixposts2c SABROWS-2). Matrix figure: OWED to the fixposts2d mechrows cloud run (scripts/cloudrun --owner main --kind mechrows --rows S474,S711,S3012 --name fixposts2d-mech). Former detector (g2pres) retired. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3012."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (r && p->stretch && o >= r->start && o < r->start + r->len && o != rs)
            continue;                   /* inside R: the run decision'"'"'s one */'
SAB_AFTER='        (void)o; (void)rs;   /* SABOTAGE S3012 */'
SAB_REACH='LIB="$TREE/build/libpcrec.a" TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_win.sh" --reach'
SAB_REACH_EXPECT="REACH-G2W-INRUN"
