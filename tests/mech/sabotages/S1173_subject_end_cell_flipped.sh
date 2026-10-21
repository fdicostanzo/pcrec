#!/usr/bin/env bash
# S1173 ([DD-11.5] P2d, lane ctxp2d) -- ONE CELL OF SUBJECT_END FLIPPED: the
# (prev in, next in) cell is 1, with the stated hex updated. `\z` then holds
# at an interior position whose two neighbours are both in the row's set. The
# set is EMPTY, so no position has an `in` neighbour and no answer moves; but
# the row now reads membership, so `cr_ctx_reads` collects its empty set and
# assertions §1d's twin stamps go red, beside CK-8, which names the row and
# the cell for `(?![\s\S])` and `\z`.
#
# P2e (lane ctxp2e, 2026-10-20): the row now also states its CLASS, which the
# build derives from the grid and checks (a flipped pin cell is no pin, so the
# grid alone would be BUILD-REFUSED, S1186's detector). The second site writes
# the class the flipped grid derives (CONTEXT), so the tree builds and CK-8
# stays this row's detector: it names the cell AND the class against libpcre2.
SAB_ID="S1173-subject-end-cell-flipped"
SAB_FILE="src/core/ctxfn.def"
SAB_SUITES="assertions"
SAB_DESC='the \z row'"'"'s (prev in, next in) cell is 1; the table no longer states \z'
SAB_DOC_FIGURE='OWED (lane ctxp2d; re-measured by lane ctxp2e 2026-10-20 with the class second site): CK-8 5 failures (cell and class, the empty PIN_END class); tests/assertions/absolute.rxt 22 failed (generated C for (\z)* no longer compiles under -Werror)'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='CTXFN_ROW(SUBJECT_END, 0x124,   0,0,1, 0,0,1,  0,0,1,'
SAB_AFTER='CTXFN_ROW(SUBJECT_END, 0x134,   0,0,1, 0,1,1,  0,0,1,   /* SABOTAGE S1173 */'
SAB_FILE2="src/core/ctxfn.def"
SAB_BEFORE2='          PIN_END, VMCTX_END, NULL, false,'
SAB_AFTER2='          CONTEXT, VMCTX_END, NULL, false,   /* SABOTAGE S1173 */'
SAB_COUNT2='1'
