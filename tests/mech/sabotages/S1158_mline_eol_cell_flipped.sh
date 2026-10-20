#!/usr/bin/env bash
# S1158 ([DD-11.5] P2c SP-8, lane ctxbuild) -- ONE CELL OF ONE ROW FLIPPED:
# MLINE_EOL's (prev out, next absent) cell is 0, with the stated hex updated so
# the build accepts it. `(?m)$` then fails at the end of a subject whose last
# character is not a newline: `a(?m)$` on "a" is (0,1) in libpcre2, nomatch
# under the plant. CK-8 (tests/assertions/ctxfn_table_check.py) names the row
# and the cell; the corpus's end-of-subject `(?m)$` cells go red.
SAB_ID="S1158-mline-eol-cell-flipped"
SAB_FILE="src/core/ctxfn.def"
SAB_SUITES="assertions harness"
SAB_DESC='the (?m)$ row'"'"'s (prev out, next absent) cell is 0, so (?m)$ fails at the subject end after a non-newline'
SAB_DOC_FIGURE='MEASURED 2026-10-20 (lane ctxbuild validation, solo mech row on the Linux dev box): asrt:2fail/55pass,corpus:485fail/70760pass -- DETECTED'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='CTXFN_ROW(MLINE_EOL,   0x1B6,  0,1,1,  0,1,1,  0,1,1,'
SAB_AFTER='CTXFN_ROW(MLINE_EOL,   0x1B2,  0,1,0,  0,1,1,  0,1,1,   /* SABOTAGE S1158 */'
