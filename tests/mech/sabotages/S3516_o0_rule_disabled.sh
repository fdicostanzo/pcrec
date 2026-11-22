#!/usr/bin/env bash
# S3516 ([MEMFN] R-47 unit U3, lane bsu3fix, review r76 CHECKS-1, 2026-11-21) -- the -O0 RULE
# of C18 (block_span.md §10.2) reads nothing. S3515's plant is also rejected by the V head
# leg, so it cannot tell a deleted -O0 rule from a live one; this row disables the rule alone
# (the loop over the always_inline selectors runs over no selector) and the in-script
# V_O0_CONTROL (a level helper whose byte shuffle is replaced, heads untouched, judged by
# o0_inline_issues alone after the text legs passed it) must go red.
SAB_ID='S3516-o0-rule-disabled'
SAB_FILE='tests/memfn/simd_floor_check.py'
SAB_SUITES='simdfloor'
SAB_DESC='the -O0 rule loop runs over no selector, so a V selector whose caller holds no byte shuffle at -O0 is not seen by it'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3516. docs/dev/lanes/bsu3fix_report.md carries the lane run.'
SAB_REACH_POP='tests/memfn/simd_floor_check.py|^    for fn in sorted\(always_inline_sel\(ton\) & set\(sel\)\):$|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for fn in sorted(always_inline_sel(ton) & set(sel)):'
SAB_AFTER='    for fn in sorted(set()):   # SABOTAGE S3516'
