#!/usr/bin/env bash
# S1153 ([DD-11.5] P2c SP-4b, lane ctxbuild) -- MLINE_BOL's in/absent CELL COPIED
# FROM out (the four-cell habit), with the row's stated hex updated so the build
# accepts it: `(?m)^` then holds after a FINAL newline. Witness `(?m)^` on "a\n"
# searched from 2: libpcre2 nomatch (PCRE2_ALT_CIRCUMFLEX is what turns it on),
# the plant (2,2). CK-8 (tests/assertions/ctxfn_table_check.py) names the row
# and the cell from libpcre2.
SAB_ID="S1153-mline-bol-final-newline-cell"
SAB_FILE="src/core/ctxfn.def"
SAB_SUITES="assertions harness"
SAB_DESC='the (?m)^ row'"'"'s (prev in, next absent) cell is 1, so (?m)^ matches after a newline that ends the subject'
SAB_DOC_FIGURE='OWED: written by lane ctxbuild 2026-10-19 during a bench timing window (no mech run allowed); the post-window validation lane runs it. Read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S1153.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='CTXFN_ROW(MLINE_BOL,   0x1D8,  0,0,0,  1,1,0,  1,1,1,'
SAB_AFTER='CTXFN_ROW(MLINE_BOL,   0x1F8,  0,0,0,  1,1,1,  1,1,1,   /* SABOTAGE S1153 */'
