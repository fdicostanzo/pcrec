#!/usr/bin/env bash
# S719 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09; re-anchored by lane r14b, 2026-10-11, on the trimmed verify's render: the plant still replaces every rendering's verify, trimmed or whole) -- the pair/position filter accepting a near-miss without the verify. G2's SIMD family (its near-miss subjects).
SAB_ID='S719-vrun-verify-skipped'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the vrun in-block verify is replaced by 1: any lane passing the one-position filter is returned'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S719. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        int rc = np ? run_cmp_render_trim(art, t, "subject + cand", t->offset, proven, np, o)'
SAB_AFTER='        int rc = 1 ? (o->puts(o->u, "1"), 0)   /* SABOTAGE S719 */'
