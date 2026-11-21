#!/usr/bin/env bash
# S3130 (lane r1on, 2026-11-14; [RUN-POS-SET] stage 2a rule (1), witness S-c of
# alt_normal_form.md §5 stage 2a) -- `all` WITHOUT THE EQUAL-WIDTH TEST.
#
# `rr_alt_union` (src/facts/req.c) drops its width clause, so two `all`
# branches of DIFFERENT widths whose common head is as long as the left one
# read as one exact width: `xy(?:ab|abc)zw` claims `xyabzw` (with altcls on,
# `ab(?:|c)`'s empty-or-`c` reads as the width-0 unit, the same claim), and the
# pre-check deletes every match that takes `abc`. Detectors: the harness on
# tests/litscan/spanarms.rxt (S-c's blocks, both engines: `xyabczw` (0,7)
# answers NOMATCH) and run_facts_checks.sh [facts-ahead]'s S-c cells.
SAB_ID="S3130-alt-union-unequal-width"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness facts"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC="rr_alt row 1 claims an alternation all without testing that its branches have one width, so an unequal-width alternation over-claims the run and the pre-check deletes matches (S-c)"
SAB_DOC_FIGURE="DESIGNED by lane r1on 2026-11-14 (planted on a scratch build: docs/dev/lanes/r1on_report.md WITNESSES); no matrix figure at SUBJECT yet, OWED: the fixposts2 lane's mechrows cloud run (scripts/cloudrun --owner main --kind mechrows --rows S3129,S3130,S3131,S3132 --name fixposts2), whose verdict fills this figure. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3130."
SAB_REACH='"$PCREC" --features all -p rx --emit-main -o /dev/stdout --pattern "xy(?:ab|abc)zw" | grep -qE "RX_REQ_RUN \"78796162(@[0-9]+)?\"" && echo REACH-ALT-UNION-UNEQUAL'
SAB_REACH_EXPECT="REACH-ALT-UNION-UNEQUAL"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        r->head.n != n || l->maxw != n || r->maxw != n)'
SAB_AFTER='        0)   /* SABOTAGE S3130 */'
