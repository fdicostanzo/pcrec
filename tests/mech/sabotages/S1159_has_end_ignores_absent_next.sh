#!/usr/bin/env bash
# S1159 ([DD-11.5] P2b, lane ctxbuild) -- THE has_end HOIST STOPS READING THE ROW.
# A machine whose only `pos == n` reader is a `(?m)$` row never computes the end
# view, so the row's absent-next cells are never consulted: `a(?m)$` on "a"
# loses its end-of-subject match (libpcre2 (0,1)).
SAB_ID="S1159-has-end-ignores-absent-next"
SAB_FILE="src/ir/dfa.c"
SAB_SUITES="harness assertions"
SAB_DESC='the has_end hoist ignores context rows that read an absent next character, so (?m)$ loses the pos == n view'
SAB_DOC_FIGURE='OWED: written by lane ctxbuild 2026-10-19 during a bench timing window (no mech run allowed); the post-window validation lane runs it. Read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S1159.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            if (ctxfn_reads_absent_next(nfa->st[i].ctxfn)) has_end = true;'
SAB_AFTER='            (void)0;   /* SABOTAGE S1159 */'
