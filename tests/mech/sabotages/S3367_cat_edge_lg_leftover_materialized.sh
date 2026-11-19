#!/usr/bin/env bash
# S3367 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-L7 (span_arms §5.7, CAT-EDGE, F2 (a)): a carried `lg` leftover is
# MATERIALIZED as head bytes instead of carried as a guard.
# Detector: the harness on tests/litscan/spanarms.rxt (both engines), libpcre2-8's answers.
SAB_ID="S3367-cat-edge-lg-leftover-materialized"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='CAT-EDGE materializes a lookbehind'\''s leftover before the left factor as head bytes with `all` kept, so `y(?:x(?<=yx))z` claims `yyxz`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3367."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''y(?:x(?<=yx))z'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}79787a\t'\'' && echo REACH-WL7'
SAB_REACH_EXPECT="REACH-WL7"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    o.lg = l.all && lleft.n ? rn_guard_meet_last(w, l.lg, lleft, &empty) : l.lg;'
SAB_AFTER='    o.lg = l.lg; if (l.all && lleft.n) { o.head = rn_app(lleft, o.head); o.tail = o.head; o.best = rn_better(w, o.best, o.head); }   /* SABOTAGE S3367 */'
