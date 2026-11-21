#!/usr/bin/env bash
# S3518 ([MEMFN] R-47 unit U3, lane bsu3fix, review r76 CHECKS-3, 2026-11-21) -- the NAMED `vspan`
# witness stops reading the vector span's w32 row and renders another SIMD form instead (a
# caseless run), so the kind-blind total `simd-form-named` (9) does not drop: only the per-row
# floor `named-vspan-w32` can see it.
SAB_ID='S3518-named-vspan-reads-another-form'
SAB_FILE='tests/memfn/simd_guarded_check.py'
SAB_SUITES='simdguarded'
SAB_DESC='the named vspan witness pattern renders a vrun form, not span-vector-w32: the named-form total holds, the row is unread by the witness'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3518. docs/dev/lanes/bsu3fix_report.md carries the lane run.'
SAB_REACH_POP='tests/memfn/simd_guarded_check.py|^    \(.vspan., .\[0-9a-f\]\{17\}.\),$|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE="    ('vspan', '[0-9a-f]{17}'),"
SAB_AFTER="    ('vspan', '(?i)abcdefghijklmnop'),   # SABOTAGE S3518"
