#!/usr/bin/env bash
# S3366 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-L2 (span_arms §5.7, CAT-EDGE): a carried `rg` leftover is MATERIALIZED as
# head bytes with `all` kept, instead of carried as a guard.
# Detector: the harness on tests/litscan/spanarms.rxt (both engines), libpcre2-8's answers.
SAB_ID="S3366-cat-edge-rg-leftover-materialized"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='CAT-EDGE materializes a lookahead'\''s leftover past the right factor as head bytes with `all` kept, so `x(?:(?=abcd)ab)cd` (W-L2b) claims `xabcdcd` and loses `xabcd`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3366."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''x(?:(?=abcd)ab)cd'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}7861626364\t'\'' && echo REACH-WL2'
SAB_REACH_EXPECT="REACH-WL2"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    o.rg = r.all && rleft.n ? rn_guard_meet_first(w, r.rg, rleft, &empty) : r.rg;'
SAB_AFTER='    o.rg = r.rg; if (r.all && rleft.n) { o.head = rn_app(o.head, rleft); o.best = rn_better(w, o.best, o.head); }   /* SABOTAGE S3366 */'
# RE-AIMED 2026-11-19 (lane l1ffix, review r55 CHECK-4): W-L2's own pattern never reaches the plant (its group is
# the spine's leftmost element, so the walk flattens it and no leftover reaches CAT-EDGE); it was detected only
# through other rows. The new witness W-L2b `x(?:(?=abcd)ab)cd` (spanarms.rxt, both engines) puts the group in
# a right operand: MEASURED with the full plant (every SAB_* edit, binary rebuilt): the run moves 7861626364 ->
# 78616263646364 and 2 of its 3 cells go red; the subject passes all 3.
