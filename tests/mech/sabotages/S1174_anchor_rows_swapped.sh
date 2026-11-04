#!/usr/bin/env bash
# S1174 ([DD-11.5] P2d, lane ctxp2d; RE-AIMED at P2e, lane ctxp2e) -- THE
# SUBJECT PINS SWAP THEIR ROWS AT THE PRODUCER: `\A` builds the SUBJECT_END
# row and `\z` the SUBJECT_START row. P2d planted the one AST-kind->row map
# (`pcrec_anchor_ctxfn`), which P2e deleted: the producer now writes the row
# on the node, so the swap moves to mod_assertions.c's two builders (a plain
# `^` is parse.c's and keeps its row). Every engine and every analysis reads
# the node, so all answer wrong together: `\Aa` on "a" is (0,1) in libpcre2,
# nomatch under the plant.
# RE-PLANTED 2026-11-04 (lane mechfix1): the swap (\A builds the END row, \z the START row)
# makes `a\z` / `\Aa` unsatisfiable, and an unsatisfiable pattern's prefilter leaves
# `window` uninitialised in the artifact (-Werror=maybe-uninitialized: ANOMALY). The plant is now
# the one-sided wrong row that stays satisfiable: `\z` is built as `\Z` (A_EOL, end or before a
# final newline), so `a\z` on "a\n" is (0,1) under the plant and nomatch in libpcre2.
SAB_ID="S1174-anchor-rows-swapped"
SAB_FILE="src/parse/mod_assertions.c"
SAB_SUITES="harness assertions"
SAB_DESC='the assertions port builds \z as the \Z kind (A_EOL) instead of the SUBJECT_END row, so \z also holds before a final newline'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='        k = A_CTX; pin = CTXFN_SUBJECT_END; break;'
SAB_AFTER='        k = A_EOL; break;   /* SABOTAGE S1174 */'
