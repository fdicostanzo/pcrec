#!/usr/bin/env bash
# S2993 -- span_pick unit 3.0a (docs/design/memfn/plan_frame.md rev 2.2 §5 row (R), [rev2 F9, F21]; lane s30a).
# THE SUPPORT TABLE'S PAIR ROW ADMITS SHIFT AS WELL.
#
# Plant: PAIR feeds RESTART and SHIFT, so on E-find Table S's intersection is {RESTART, SHIFT}: ST-many, the named
# refusal. RE-MODELLED at the r1 s30a review fixes (lane s30arev, F1): the refusal is raised only where Table E
# answers E-find, so the site is not refused: Table E's legacy-first order serves it on another frame (E-stmt's
# walk, `(?:(?!a)z|w)` -> pf_walk_bounded) or pcrec renders another form (`a[Xx].b`, its FUNC form): a SILENT
# MOVE, measured 12 of 60 (pattern, arm) compiles, rc 0 on every one; `foo|bar\d` (E-stmt) does not move.
# Detector (re-aimed from the corpus harness, whose answers a correct other text does not change):
# tests/memfn/run_finder.sh (arm memfnfinder): the PAIR form no longer resolves (mf_form_hash(pair) -1, the form
# floor, the kit-grid cards and store rows naming form pair). rows_check.py §R (the B-pair and B-fn witnesses'
# triples) and §S (the PAIR pin row) are red too (make test's test-memfn-rows; no mech arm runs rows_check).
SAB_ID="S2993-support-pair-two-streams"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='the support table says PAIR feeds RESTART and SHIFT: Table S answers ST-many on E-find and its B-pair sites move to another frame or form'
SAB_DOC_FIGURE='MEASURED 2026-11-09 BY HAND, planted by hand on a git archive of lane/memfn-s30a c8d54df7c (lane s30arev, review r1 s30a fixes), built with nice make -j2; 15 patterns x 4 arms compiled by the planted and the clean pcrec and classed: SILENT-MOVE 12, SAME 48, LOUD 0; memfnfinder 17fail/3295pass (form pair unresolved); rows_check 7 failed. Earlier: lane s30a LOUD (the witnesses refused) before F1. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S2993.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "PAIR",      FF_PAIR,      WF_ST_RESTART,'
SAB_AFTER='    { "PAIR",      FF_PAIR,      WF_ST_RESTART | WF_ST_SHIFT,   /* SABOTAGE S2993 */'
