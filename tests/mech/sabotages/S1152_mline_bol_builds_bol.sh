#!/usr/bin/env bash
# S1152 ([DD-11.5] P2c SP-4, lane ctxbuild) -- THE PARSER BUILDS A_BOL FOR (?m)^,
# the D62 failure in its new form: the `(?m)` choice of node is skipped, so a
# multiline `^` is the subject-start anchor. Witness `(?m)^b` on "a\nb":
# libpcre2 (2,3), the plant nomatch (ctx_span.md §6 CK-4 SP-4; revision 1's
# `(?m)^$` on "a\n" does not reach).
# RE-PLANTED 2026-11-04 (lane mechfix1): the first plant built A_BOL, which makes
# `(?m)(\n^)` unmatchable and the prefilter's `window` provably uninitialised
# (-Werror=maybe-uninitialized in the artifact: ANOMALY). The wrong ROW instead of
# the wrong NODE keeps every pattern satisfiable; `(?m)^b` on "a\nb" still
# fails (the row now wants a newline AFTER the position).
SAB_ID="S1152-mline-bol-builds-bol"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness assertions"
SAB_DESC='`(?m)^` is built with the MLINE_EOL context row instead of MLINE_BOL, so it holds before a newline and not after one'
SAB_DOC_FIGURE='MEASURED 2026-10-20 (lane ctxbuild validation, solo mech row on the Linux dev box): corpus:237fail/71008pass,asrt:0fail/57pass -- DETECTED'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
# RE-ANCHORED 2026-11-11 (lane ucfix): [UCP] U3 made the site a ternary (`reg_at` rides the node).
SAB_BEFORE='        Ast *a = cx->mods->multiline ? mline_ctx(cx, CTXFN_MLINE_BOL, apos)'
SAB_AFTER='        Ast *a = cx->mods->multiline ? mline_ctx(cx, CTXFN_MLINE_EOL, apos)   /* SABOTAGE S1152: (?m)^ reads the line-end row */'
