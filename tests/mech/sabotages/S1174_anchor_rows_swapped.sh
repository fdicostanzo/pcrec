#!/usr/bin/env bash
# S1174 ([DD-11.5] P2d, lane ctxp2d; RE-AIMED at P2e, lane ctxp2e) -- THE
# SUBJECT PINS SWAP THEIR ROWS AT THE PRODUCER: `\A` builds the SUBJECT_END
# row and `\z` the SUBJECT_START row. P2d planted the one AST-kind->row map
# (`pcrec_anchor_ctxfn`), which P2e deleted: the producer now writes the row
# on the node, so the swap moves to mod_assertions.c's two builders (a plain
# `^` is parse.c's and keeps its row). Every engine and every analysis reads
# the node, so all answer wrong together: `\Aa` on "a" is (0,1) in libpcre2,
# nomatch under the plant.
SAB_ID="S1174-anchor-rows-swapped"
SAB_FILE="src/parse/mod_assertions.c"
SAB_SUITES="harness assertions"
SAB_DESC='the assertions port builds \A as the SUBJECT_END row and \z as the SUBJECT_START row'
SAB_DOC_FIGURE='OWED (lane ctxp2e): reach measured by hand, see docs/dev/lanes/ctxp2e_report.md §5'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='        k = A_CTX; pin = CTXFN_SUBJECT_START; pcrec_lb_raise(cx, 1); break;'
SAB_AFTER='        k = A_CTX; pin = CTXFN_SUBJECT_END; pcrec_lb_raise(cx, 1); break;   /* SABOTAGE S1174 */'
SAB_FILE2="src/parse/mod_assertions.c"
SAB_BEFORE2='        k = A_CTX; pin = CTXFN_SUBJECT_END; break;'
SAB_AFTER2='        k = A_CTX; pin = CTXFN_SUBJECT_START; break;   /* SABOTAGE S1174 */'
SAB_COUNT2='1'
