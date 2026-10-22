#!/usr/bin/env bash
# S1415 (D172 S2 commit 5, lane wsc5) -- C-PIN'S CLAUSE 4 DROPPED IN THE
# WINDOW FAMILY (memfn/src/window.c `c_pin`): the family pins the run R even
# where its plan ALREADY tests all of R through the other spans (class A), so
# the reply carries C-pin and keyword `in|instanceof` takes `run-pinned`
# instead of keeping `offset-set`.
#
# SUCCESSOR of S281 (retired at commit 5): S281 planted the same clause in
# the planner's pick (`pf_run_applies_common`, later `nk_pick_run_pinned`),
# which since the lever's default flipped decides only under the inverse
# lever `window-legacy` (deleted at commit 6); the default NEXT reads the family's reply,
# so the clause the default build reads is this one (window_site.md rev 3.2
# §2.3 C-pin, §2.4). Same witness, same detector, same intent.
#
# ANSWER-INVISIBLE: the run row's test is sound on class A too; the detector
# is structural (prechecks §5.10's stamp expectation).
SAB_ID="S1415-cpin-clause4-dropped"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="prechecks"
SAB_DESC="the window family's C-pin no longer declines a plan that already tests all of R through its other spans (clause 4), so class A artifacts (whose offset-set selection already verifies the pinned run) move to run-pinned: keyword in|instanceof stamps run-pinned instead of offset-set"
SAB_DOC_FIGURE="Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1415."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "in|instanceof" && grep -q "^#define RX_DFA_PREFILTER \"offset-set\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_WHY \"dominated\"" "$REACH_TMP/o.c" && echo REACH-CLASS-A-KEYWORD'
SAB_REACH_EXPECT="REACH-CLASS-A-KEYWORD"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (all) return;'
SAB_AFTER='    if (0 && all) return;   /* SABOTAGE S1415 */'
