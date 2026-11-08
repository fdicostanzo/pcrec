#!/usr/bin/env bash
# S2993 -- span_pick unit 3.0a (docs/design/memfn/plan_frame.md rev 2.2 §5 row (R), [rev2 F9, F21]; lane s30a).
# THE SUPPORT TABLE'S PAIR ROW ADMITS SHIFT AS WELL.
#
# Plant: PAIR feeds RESTART and SHIFT, so on E-find Table S's intersection is {RESTART, SHIFT}: ST-many. T-FIND's
# gate holds (ST-many is renderable) and the decision is then REFUSED by the named ST-many refusal (fd_find's
# `?stream`; wf_plan_site's "Table S answers ST-many"), never a silent move to B-walk: every B-pair and B-fn site
# is refused, and pcrec fails the compile.
# Detector: the corpus (arm harness): every pattern with an E-find two-byte stop fails to compile (measured by
# lane s30a: `foo|bar\d`, `(?:(?!a)z|w)`, `(?:(?i:abs)|(?i:ab)S)` rc 1). rows_check.py §R's refusal invariant
# names it ("REFUSED naming Table S's ST-many refusal") and §S is red too (no mech arm runs rows_check).
SAB_ID="S2993-support-pair-two-streams"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="harness"
SAB_DESC='the support table says PAIR feeds RESTART and SHIFT: Table S answers ST-many on E-find and every B-pair site is refused'
SAB_DOC_FIGURE='MEASURED by lane s30a 2026-11-07, planted and reverted by hand (the witnesses refused, rows_check red); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2993.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "PAIR",      FF_PAIR,      WF_ST_RESTART,'
SAB_AFTER='    { "PAIR",      FF_PAIR,      WF_ST_RESTART | WF_ST_SHIFT,   /* SABOTAGE S2993 */'
