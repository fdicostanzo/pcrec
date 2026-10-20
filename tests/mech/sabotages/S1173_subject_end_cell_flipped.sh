#!/usr/bin/env bash
# S1173 ([DD-11.5] P2d, lane ctxp2d) -- ONE CELL OF SUBJECT_END FLIPPED: the
# (prev in, next in) cell is 1, with the stated hex updated. `\z` then holds
# at an interior position whose two neighbours are both in the row's set. The
# set is EMPTY, so no position has an `in` neighbour and no answer moves; but
# the row now reads membership, so `cr_ctx_reads` collects its empty set and
# assertions §1d's twin stamps go red, beside CK-8, which names the row and
# the cell for `(?![\s\S])` and `\z`.
SAB_ID="S1173-subject-end-cell-flipped"
SAB_FILE="src/core/ctxfn.def"
SAB_SUITES="assertions"
SAB_DESC='the \z row'"'"'s (prev in, next in) cell is 1; the table no longer states \z'
SAB_DOC_FIGURE='OWED (lane ctxp2d): by hand 2026-10-20, CK-8 2 failures, assertions §1d 0 pass / 4 fail, tests/assertions/absolute.rxt 0 failed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='CTXFN_ROW(SUBJECT_END, 0x124,   0,0,1, 0,0,1,  0,0,1,'
SAB_AFTER='CTXFN_ROW(SUBJECT_END, 0x134,   0,0,1, 0,1,1,  0,0,1,   /* SABOTAGE S1173 */'
