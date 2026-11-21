#!/usr/bin/env bash
# S3377 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-E1 (span_arms §4.5, §5.7): E-5i's row admits a NEGATIVE lookaround, whose
# body is then read as a positive item.
# Detector: the harness on tests/litscan/spanarms.rxt (both engines), libpcre2-8's answers.
SAB_ID="S3377-negative-body-read-as-item"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='a negative lookaround'\''s body is read as a positive item, so `x(?!ab)a[bc]` narrows `[bc]` to `b` and deletes `xac`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3377."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''x(?!ab)a[bc]'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}786162/fffffe\t'\'' && echo REACH-WE1'
SAB_REACH_EXPECT="REACH-WE1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (a->k == A_LOOK) return !a->u.look.neg;'
SAB_AFTER='    if (a->k == A_LOOK) return true;   /* SABOTAGE S3377 */'
