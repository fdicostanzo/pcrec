#!/usr/bin/env bash
# S3368 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-L6 (span_arms §5.7, CAT-EDGE across a non-`all` neighbour): the leftover
# crosses a variable-width neighbour, shifted by its maximum width, instead
# of being dropped.
# Detector: the harness on tests/litscan/spanarms.rxt (both engines), libpcre2-8's answers.
SAB_ID="S3368-cat-edge-carried-across-non-all"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='CAT-EDGE carries a lookahead'\''s leftover across a right factor that is not `all`, shifted by its width, so `(?:(?=abc)a.?)[bc]c` narrows `[bc]` to `c` and deletes `abc`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3368."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''(?:(?=abc)a.?)[bc]c'\'' | grep -qP '\''^byte\treq_set_maxoff\t([^\t]*\t){4}97:0,99:3\t'\'' && echo REACH-WL6'
SAB_REACH_EXPECT="REACH-WL6"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    o.rg = r.all && rleft.n ? rn_guard_meet_first(w, r.rg, rleft, &empty) : r.rg;'
SAB_AFTER='    o.rg = r.all && rleft.n ? rn_guard_meet_first(w, r.rg, rleft, &empty) : rleft.n && r.maxw - r.head.n >= 0 && r.maxw - r.head.n < rleft.n ? rn_slice(&rleft, (int)(r.maxw - r.head.n), rleft.n) : r.rg;   /* SABOTAGE S3368 */'
