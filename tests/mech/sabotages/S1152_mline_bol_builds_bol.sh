#!/usr/bin/env bash
# S1152 ([DD-11.5] P2c SP-4, lane ctxbuild) -- THE PARSER BUILDS A_BOL FOR (?m)^,
# the D62 failure in its new form: the `(?m)` choice of node is skipped, so a
# multiline `^` is the subject-start anchor. Witness `(?m)^b` on "a\nb":
# libpcre2 (2,3), the plant nomatch (ctx_span.md §6 CK-4 SP-4; revision 1's
# `(?m)^$` on "a\n" does not reach).
SAB_ID="S1152-mline-bol-builds-bol"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness assertions"
SAB_DESC='`(?m)^` is built as A_BOL (the subject start) instead of the MLINE_BOL context node, so it never matches after a newline'
SAB_DOC_FIGURE='OWED: written by lane ctxbuild 2026-10-19 during a bench timing window (no mech run allowed); the post-window validation lane runs it. Read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S1152.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='        if (cx->mods->multiline) return mline_ctx(cx, CTXFN_MLINE_BOL, apos);'
SAB_AFTER='        (void)0;   /* SABOTAGE S1152: (?m)^ builds A_BOL */'
