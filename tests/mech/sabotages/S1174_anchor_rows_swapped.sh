#!/usr/bin/env bash
# S1174 ([DD-11.5] P2d, lane ctxp2d) -- THE ANCHOR-KIND MAP SWAPS ITS ROWS:
# `pcrec_anchor_ctxfn` gives `^`/`\A` the SUBJECT_END row and `\z` the
# SUBJECT_START row. Both engines read the one map, so both answer wrong
# together: `^a` on "a" is (0,1) in libpcre2, nomatch under the plant. The
# corpus's oracle-verified `^`/`\A`/`\z` cells go red on every arm.
SAB_ID="S1174-anchor-rows-swapped"
SAB_FILE="src/core/internal.h"
SAB_SUITES="harness assertions"
SAB_DESC='pcrec_anchor_ctxfn maps A_BOL to SUBJECT_END and A_END to SUBJECT_START'
SAB_DOC_FIGURE='OWED (lane ctxp2d): by hand 2026-10-20, tests/assertions/absolute.rxt 237 failed, assertions §1d 0 pass / 4 fail'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    return k == A_BOL ? CTXFN_SUBJECT_START : k == A_END ? CTXFN_SUBJECT_END : 0;'
SAB_AFTER='    return k == A_BOL ? CTXFN_SUBJECT_END : k == A_END ? CTXFN_SUBJECT_START : 0;   /* SABOTAGE S1174 */'
