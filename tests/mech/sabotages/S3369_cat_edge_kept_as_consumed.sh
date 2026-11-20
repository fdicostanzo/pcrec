#!/usr/bin/env bash
# S3369 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-L8 (span_arms §5.7, CAT-EDGE, F2 (f)): a leftover at a non-`all` left
# neighbour is kept as consumed text instead of dropped.
# Detector: the harness on tests/litscan/spanarms.rxt (both engines), libpcre2-8's answers.
SAB_ID="S3369-cat-edge-kept-as-consumed"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='a lookbehind'\''s leftover at a left neighbour that is not `all` is kept as CONSUMED bytes, so `y*(?:ab(?<=xab)c)` claims `xabc` and a search from 1 finds none'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3369."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''y*(?:ab(?<=xab)c)'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}616263\t'\'' && echo REACH-WL8'
SAB_REACH_EXPECT="REACH-WL8"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    o.lg = l.all && lleft.n ? rn_guard_meet_last(w, l.lg, lleft, &empty) : l.lg;'
SAB_AFTER='    o.lg = l.all && lleft.n ? rn_guard_meet_last(w, l.lg, lleft, &empty) : l.lg; if (!l.all && lleft.n) o.best = rn_better(w, o.best, rn_app(lleft, r.head));   /* SABOTAGE S3369 */'
