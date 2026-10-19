#!/usr/bin/env bash
# S1156 ([DD-11.5] P2b, lane ctxbuild; B3/A4) -- POSSESSIFY NARROWS AN ABSENT-READING
# ROW. `pcrec_poss_ctx_admits` loses its decline, so arm A values `(?m)^`/`(?m)$`
# gates from their membership cells alone, handing `First` readers a false
# non-nullable (valuing them is UL-c, its own event). Detector:
# tests/possessify/ctx_admits_check.c (every absent-reading row of the 512 must
# answer no-narrowing; run_possessify_tests.sh section 10). The answer-level
# witnesses are the A4 cells ctx_span.md §4.2.5 names (`a{0,3}(?m)$`,
# `(?m)^a+b`, `[a\n]+(?m)$\n`), owed to tests/possessify/.
SAB_ID="S1156-poss-absent-row-narrows"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="possdiff harness"
SAB_DESC='pcrec_poss_ctx_admits narrows a context row that reads an absent side, so (?m)^/(?m)$ gates are valued from membership alone'
SAB_DOC_FIGURE='OWED: written by lane ctxbuild 2026-10-19 during a bench timing window (no mech run allowed); the post-window validation lane runs it. Read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S1156.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    if (ctxfn_reads_absent_prev(fn) || ctxfn_reads_absent_next(fn))'
SAB_AFTER='    if (0)   /* SABOTAGE S1156 */'
