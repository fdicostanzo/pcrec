#!/usr/bin/env bash
# S1176 ([DD-11.5] P2d, lane ctxp2d) -- THE NFA's ABSENT-ONLY FRAGMENT DROPS
# ITS ROW: `frag_ctx_row` leaves `ctxfn` 0, the function no position passes,
# so every DFA-routed `^`/`\A`/`\z` dies in the closure (and `pcrec_nfa_has_bot`
# no longer sees `^`, which moves it to ENG_UNANCH). `^a` on "a" is (0,1) in
# libpcre2, nomatch under the plant; the VM is untouched.
SAB_ID="S1176-ctx-row-frag-drops-fn"
SAB_FILE="src/ir/nfa.c"
SAB_SUITES="harness assertions"
SAB_DESC='the NFA lowers ^/\A/\z to an N_CTX state with truth function 0'
SAB_DOC_FIGURE='OWED (lane ctxp2d): by hand 2026-10-20, tests/assertions/absolute.rxt 193 failed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    b->nfa->st[f.start].ctxfn = fn;'
SAB_AFTER='    b->nfa->st[f.start].ctxfn = 0; (void)fn;   /* SABOTAGE S1176 */'
