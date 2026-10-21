#!/usr/bin/env bash
# S1172 ([DD-11.5] P2d, lane ctxp2d) -- ONE CELL OF SUBJECT_START FLIPPED:
# the (prev absent, next absent) cell is 0, with the stated hex updated so the
# build accepts it. `^`/`\A` then fail on the EMPTY subject: `^$` and `\A\z`
# on "" are (0,0) in libpcre2, nomatch under the plant. CK-8
# (tests/assertions/ctxfn_table_check.py) names the row and the cell, for the
# canonical spelling and both native ones; the corpus's empty-subject `^`
# cells go red.
#
# P2e (lane ctxp2e, 2026-10-20): the row now also states its CLASS, which the
# build derives from the grid and checks (a flipped pin cell is no pin, so the
# grid alone would be BUILD-REFUSED, S1186's detector). The second site writes
# the class the flipped grid derives (CONTEXT), so the tree builds and CK-8
# stays this row's detector: it names the cell AND the class against libpcre2.
SAB_ID="S1172-subject-start-cell-flipped"
SAB_FILE="src/core/ctxfn.def"
SAB_SUITES="assertions harness"
SAB_DESC='the \A/^ row'"'"'s (prev absent, next absent) cell is 0, so ^ fails on the empty subject'
SAB_DOC_FIGURE='OWED (lane ctxp2d; re-measured by lane ctxp2e 2026-10-20 with the class second site): CK-8 7 failures (cell and class, both native spellings, the empty PIN_START class), tests/assertions/absolute.rxt 5 failed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='CTXFN_ROW(SUBJECT_START, 0x1C0, 0,0,0, 0,0,0,  1,1,1,'
SAB_AFTER='CTXFN_ROW(SUBJECT_START, 0x0C0, 0,0,0, 0,0,0,  1,1,0,   /* SABOTAGE S1172 */'
SAB_FILE2="src/core/ctxfn.def"
SAB_BEFORE2='          PIN_START, VMCTX_START, NULL, false,'
SAB_AFTER2='          CONTEXT, VMCTX_START, NULL, false,   /* SABOTAGE S1172 */'
SAB_COUNT2='1'
