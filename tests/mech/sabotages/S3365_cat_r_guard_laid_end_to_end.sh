#!/usr/bin/env bash
# S3365 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-L5 (span_arms §5.7, CAT-R): the guard is laid END TO END with the right
# factor (rev 0's text) instead of met at its first positions.
# Detector: the harness on tests/litscan/spanarms.rxt (both engines), libpcre2-8's answers.
SAB_ID="S3365-cat-r-guard-laid-end-to-end"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='CAT-R lays a lookahead'\''s guard end to end with the right factor instead of meeting its first positions, so `xy(?=bc)[bc]c` claims `xybc[bc]c` and the pre-check deletes `xybc`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3365."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''xy(?=bc)[bc]c'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}78796263\t'\'' && echo REACH-WL5'
SAB_REACH_EXPECT="REACH-WL5"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    RbRun rleft = rn_guard_onto_head(w, &r, l.rg, &empty);   /* CAT-R */'
SAB_AFTER='    RbRun rleft = rn_none(); if (l.rg.n) { r.head = rn_app(l.rg, r.head); if (r.all) r.tail = r.best = r.head; }   /* SABOTAGE S3365 */'
