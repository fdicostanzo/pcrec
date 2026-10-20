#!/usr/bin/env bash
# S1172 ([DD-11.5] P2d, lane ctxp2d) -- ONE CELL OF SUBJECT_START FLIPPED:
# the (prev absent, next absent) cell is 0, with the stated hex updated so the
# build accepts it. `^`/`\A` then fail on the EMPTY subject: `^$` and `\A\z`
# on "" are (0,0) in libpcre2, nomatch under the plant. CK-8
# (tests/assertions/ctxfn_table_check.py) names the row and the cell, for the
# canonical spelling and both native ones; the corpus's empty-subject `^`
# cells go red.
SAB_ID="S1172-subject-start-cell-flipped"
SAB_FILE="src/core/ctxfn.def"
SAB_SUITES="assertions harness"
SAB_DESC='the \A/^ row'"'"'s (prev absent, next absent) cell is 0, so ^ fails on the empty subject'
SAB_DOC_FIGURE='OWED (lane ctxp2d): by hand 2026-10-20, CK-8 3 failures, tests/assertions/absolute.rxt 5 failed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='CTXFN_ROW(SUBJECT_START, 0x1C0, 0,0,0, 0,0,0,  1,1,1,'
SAB_AFTER='CTXFN_ROW(SUBJECT_START, 0x0C0, 0,0,0, 0,0,0,  1,1,0,   /* SABOTAGE S1172 */'
