#!/usr/bin/env bash
# S3376 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-C1 (span_arms §5.7, ITEM, `A_CTX`): PREV read as NEXT.
# Detector: the harness on tests/litscan/spanarms.rxt (both engines), libpcre2-8's answers.
SAB_ID="S3376-ctx-prev-read-as-next"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='a one-character lookbehind'\''s context node (PREV) is read as NEXT, so `ab(?<=b)[bc]d\w*e` narrows `[bc]` to `b` and deletes `abcde`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3376."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''ab(?<=b)[bc]d\w*e'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}61626264/fffffeff\t'\'' && echo REACH-WC1'
SAB_REACH_EXPECT="REACH-WC1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (a->u.ctx.fn == CTXFN_NEXT) u->rg = rn_pos(w, s);'
SAB_AFTER='    if (a->u.ctx.fn == CTXFN_NEXT || a->u.ctx.fn == CTXFN_PREV) u->rg = rn_pos(w, s);   /* SABOTAGE S3376 */'
