#!/usr/bin/env bash
# S794 ([MEMFN] R-14, lane r14b, 2026-10-11) -- the trim treating KB as proven when the KB deny is set. G2's SIMD family (the deny-kb class's answers and verify reads).
SAB_ID='S794-vrun-trim-kb-under-deny'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the trim takes the first ranked position other than the scanned one as proven even where --memfn=no-vrun-kb kept it out of the filter'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S794. docs/dev/lanes/r14b_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (k2 >= 0) proven[np++] = k2 - off;'
SAB_AFTER='    for (unsigned i = 0; i < x->p->rank_n; i++) if (x->p->rank_pos[i] != x->k - off) { proven[np++] = x->p->rank_pos[i]; break; }   /* SABOTAGE S794 */'
