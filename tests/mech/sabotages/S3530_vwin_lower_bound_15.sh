#!/usr/bin/env bash
# S3530 -- plant (c) of block_span.md §10.2 (R-47 unit U4, lane bsu4p, 2026-11-22): T-vwin's lower bound becomes 15. The bound is also the safety floor (no 16-byte block fits a shorter stretch, §4.2): the plant admits the 15-position stretch of [0-9a-f]{16}, whose renderer refuses it (the K >= 16 assert), so the compile of that cell fails. Caught by the T-table pin cells 1-2 (tests/memfn/span_pins.py, run inside C18, arm simdfloor).
SAB_ID='S3530-vwin-lower-bound-15'
SAB_FILE='memfn/src/window.c'
SAB_SUITES='simdfloor'
SAB_DESC='the vector span'\''s T-vwin admits a stretch of 15 positions (its lower bound becomes 15), below the smallest block of the level block'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3530. docs/dev/lanes/bsu4p_report.md carries the lane run.'
SAB_REACH='for p in "[0-9a-f]{16}" "[0-9a-f]{17}"; do if "$PCREC" --features all -fmemfn-simd=x86-64-v3 -p rxa -o - --pattern "$p" | grep -q "_vs0("; then echo "V-PRESENT $p"; else echo "V-ABSENT $p"; fi; done'
SAB_REACH_EXPECT='V-ABSENT [0-9a-f]{16}
V-PRESENT [0-9a-f]{17}'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return fd_brow_is(x->w->brow, FD_NAMED_DHORS) && x->k >= WF_VWIN_LO &&'
SAB_AFTER='    return fd_brow_is(x->w->brow, FD_NAMED_DHORS) && x->k >= WF_VWIN_LO - 1 &&   /* SABOTAGE S3530 */'
