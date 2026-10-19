#!/usr/bin/env bash
# S1157 ([DD-11.5] P2b, lane ctxbuild; C6) -- pcrec_nfa_has_bot STOPS READING THE
# ROW. A `(?m)^` no longer routes to ENG_ATTEMPT, so ENG_UNANCH builds a reverse
# machine that meets the MLINE_BOL row: the closure's routing assertion refuses
# the compile ("a reverse DFA met a context row that reads an absent previous
# character"), and every DFA `(?m)^` corpus cell fails.
SAB_ID="S1157-has-bot-ignores-mline-bol"
SAB_FILE="src/ir/nfa.c"
SAB_SUITES="harness assertions"
SAB_DESC='the BOT-family routing predicate ignores context rows that read an absent previous character, so (?m)^ leaves ENG_ATTEMPT'
SAB_DOC_FIGURE='OWED: written by lane ctxbuild 2026-10-19 during a bench timing window (no mech run allowed); the post-window validation lane runs it. Read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S1157.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            (nfa->st[i].k == N_CTX && ctxfn_reads_absent_prev(nfa->st[i].ctxfn)))'
SAB_AFTER='            (0 && nfa->st[i].k == N_CTX))   /* SABOTAGE S1157 */'
