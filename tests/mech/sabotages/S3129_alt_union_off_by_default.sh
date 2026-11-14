#!/usr/bin/env bash
# S3129 (lane r1on, 2026-11-14; [RUN-POS-SET] stage 2a rule (1), alt_normal_form.md
# §6 row 1, default since abi 107) -- RULE (1) IS OFF IN THE DEFAULT.
#
# `rr_alt_union` (src/facts/req.c) never applies, so every alternation falls to
# row 2 (common head and tail, never `all`): the walk is the one the
# restored walk arm `alt` runs, on every compile. No answer moves (row 2 is
# today's sound form), so the detector is the claim: tests/codegen/
# run_facts_checks.sh [facts-ahead]'s default rule (1) cells (`xy(?:ab|ac)zw`
# with altcls denied lists `61627a77` where `787961627a77` is due, and the
# census mover-class cells beside it).
SAB_ID="S3129-alt-union-off-by-default"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC="the alternation's equal-width row (rr_alt row 1, alt_union) never applies, so the default walk is the restored arm alt: an equal-width all-branch alternation no longer contributes its per-position union to the necessary run"
SAB_DOC_FIGURE="DESIGNED by lane r1on 2026-11-14; MEASURED by the lane's mechrows cloud run (docs/dev/lanes/r1on_report.md OWED). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3129."
SAB_REACH='"$PCREC" --features all -fno-altcls-merge -fno-altcls-factor -p rx --emit-main -o /dev/stdout --pattern "xy(?:ab|ac)zw" | grep -qE "RX_REQ_RUN \"787961627a77(@[0-9]+)?/fffffffeffff\"" && echo REACH-ALT-UNION-DEFAULT'
SAB_REACH_EXPECT="REACH-ALT-UNION-DEFAULT"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!l->all || !r->all || l->head.trunc || r->head.trunc ||'
SAB_AFTER='    if (1 || !l->all || !r->all || l->head.trunc || r->head.trunc ||   /* SABOTAGE S3129 */'
