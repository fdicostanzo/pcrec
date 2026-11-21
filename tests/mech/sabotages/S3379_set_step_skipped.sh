#!/usr/bin/env bash
# S3379 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-S4 (span_arms §5.7, CAT-SET): the narrowed byte is not put in the set.
# Detector: tests/codegen/reqcube_check.py check 4 (WIT row `ws4`), inside the codegen suite.
SAB_ID="S3379-set-step-skipped"
SAB_FILE="src/facts/req.c"
SAB_SUITES="codegen"
SAB_DESC='the TOP set step adds no byte, so a narrowed run position'\''s byte is not in the necessary set: `x(?=qr)[pq]r` states RX_REQ_BYTE 113 outside req_set (reqcube_check.py check 4)'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3379."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''x(?=qr)[pq]r'\'' | grep -qP '\''^byte\treq_set\t([^\t]*\t){4}113,114,120\t'\'' && echo REACH-WS4'
SAB_REACH_EXPECT="REACH-WS4"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (rb_has(set, b)) continue;'
SAB_AFTER='        continue;   /* SABOTAGE S3379 */'
