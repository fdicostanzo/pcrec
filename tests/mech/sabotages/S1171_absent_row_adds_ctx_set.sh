#!/usr/bin/env bash
# S1171 ([DD-11.5] P2d, lane ctxp2d) -- AN ABSENT-ONLY ROW ADDS A SET TO THE
# CLASS AXIS. `cr_ctx_reads` drops its `ctxfn_reads_membership` clause, so a
# `\z` (SUBJECT_END) state contributes its empty set to the context list; the
# machine then counts as carrying a word context (`clsctx`), the D11 views
# flag turns on and the candidate scan changes form. Answer-identical: no
# corpus pattern moves (0 of 4,636 under this plant, 2026-10-20), so the
# detector is assertions §1d's twin check (`a(?:\z|)` and `(?:\z)?a` stamp
# RX_DFA_PREFILTER `memchr-bounded` where their twin `a` stamps `memchr`).
SAB_ID="S1171-absent-row-adds-ctx-set"
SAB_FILE="src/ir/dfa.c"
SAB_SUITES="assertions"
SAB_DESC='a context row that reads no membership (\z'"'"'s SUBJECT_END) contributes its empty set to the class axis, flipping the views flag'
SAB_DOC_FIGURE='OWED (lane ctxp2d, light only): the plant'"'"'s reach measured by hand 2026-10-20 -- assertions §1d 0 pass / 4 fail under it'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='{ return st->k == N_CTX && ctxfn_reads_membership(st->ctxfn); }'
SAB_AFTER='{ return st->k == N_CTX; }   /* SABOTAGE S1171 */'
