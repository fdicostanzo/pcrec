#!/usr/bin/env bash
# S3132 (lane r1on, 2026-11-14; [RUN-POS-SET] stage 2a rule (1)) -- THE UNION IS
# ONE BRANCH'S RUN.
#
# `rr_alt_union` (src/facts/req.c) takes the LEFT branch's run as the
# alternation's instead of the per-position union of both, so the run claims
# bytes only the left branch matches: `((a)|b){3}c` (a census mover, class 2)
# claims `aaac` and the pre-check deletes every match that takes a `b`.
# Detector: the harness on tests/rungselect/rungselect.rxt, whose
# `((a)|b){3}c` block carries `b` subjects.
SAB_ID="S3132-alt-union-left-branch"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/rungselect/rungselect.rxt"
SAB_DESC="rr_alt row 1 states the left branch's run instead of the branches' per-position union, so the run claims bytes the right branch never matches and the pre-check deletes its matches"
SAB_DOC_FIGURE="DESIGNED by lane r1on 2026-11-14 (planted on a scratch build: docs/dev/lanes/r1on_report.md WITNESSES); no matrix figure at SUBJECT yet, OWED: the fixposts2 lane's mechrows cloud run (scripts/cloudrun --owner main --kind mechrows --rows S3129,S3130,S3131,S3132 --name fixposts2), whose verdict fills this figure. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3132."
SAB_REACH='"$PCREC" --features all -p rx --emit-main -o /dev/stdout --pattern "((a)|b){3}c" | grep -qE "RX_REQ_RUN \"\[6162\]\[6162\]\[6162\]63(@[0-9]+)?\"" && echo REACH-ALT-UNION-BOTH'
SAB_REACH_EXPECT="REACH-ALT-UNION-BOTH"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    RbRun u = rn_common_head(w, l->head, r->head);'
SAB_AFTER='    RbRun u = l->head;   /* SABOTAGE S3132 */'
