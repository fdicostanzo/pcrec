#!/usr/bin/env bash
# S1419 (D172 S2 commit 6, lane wsc6; the kit manager's R1) -- A WINDOW SITE'S
# RENDERER-INTERFACE FIELD ACCEPTED (memfn/src/window.c `wf_old_fields`): the
# kit stops refusing a window site that states `plan_hint` beside its window
# facts. plan_hint, plan_pos, rank_*, end_back, span_class and need are the
# kit's renderer interface since commit 6, written by the family's
# translation and by G2, never by a host (memfn.h "A WINDOW SITE STATES
# NOTHING ELSE").
#
# SUCCESSOR of S849 (W0 0 accepted on a FIND) and S1226 (an UNSTATED `absent`
# accepted), retired at commit 6 with the fields they planted in: the one
# statement rule the old fields left behind is this refusal.
#
# WHERE IT IS SEEN. No artifact moves (no pcrec builder states the field).
# tests/memfn/proof_check.c family A's refusal "a window site stating
# plan_hint" renders instead of refusing (arm memfnfinder, run_finder.sh part
# `proof`; the same text is run_proof.sh's plant S1419).
SAB_ID="S1419-window-old-field-accepted"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the window family accepts a window site stating plan_hint (a renderer-interface field, the translation's and G2's) beside its window facts, instead of refusing it naming the field"
SAB_DOC_FIGURE="Plant run 2026-10-22 (lane wsc6, run_proof.sh --plants): RED, 'A refuse a window site stating plan_hint: rendered'. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1419."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (p->plan_hint && p->plan_hint != MF_NO_PRED)
'
SAB_AFTER='    if (0)   /* SABOTAGE S1419: a renderer-interface field accepted */
'
