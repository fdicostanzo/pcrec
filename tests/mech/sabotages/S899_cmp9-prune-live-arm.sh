#!/usr/bin/env bash
# S899 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-9) -- the split derivation's prune also drops the LAST arm of every alternation, live or not, so Q loses an end-pinned arm P matches through.
SAB_ID='S899-cmp9-prune-live-arm'
SAB_FILE='src/opt/derive.c'
SAB_SUITES='compound harness'
SAB_HARNESS_TARGET='tests/compound/split.rxt'
SAB_DESC='the split derivation'\''s prune also drops the LAST arm of every alternation, live or not, so Q loses an end-pinned arm P matches through'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): compound arm 193 FAIL lines (B1/B2/G2: Q loses its last arm), harness on split.rxt 945 of 13,839 cases. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (it[i].never && !it[i].keeps) { q->pruned_arms++; continue; }'
SAB_AFTER='        if ((it[i].never && !it[i].keeps) || (i == n - 1 && n > 1)) { q->pruned_arms++; continue; }   /* SABOTAGE S899 */'
