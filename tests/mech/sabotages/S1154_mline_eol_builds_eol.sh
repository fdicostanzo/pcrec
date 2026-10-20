#!/usr/bin/env bash
# S1154 ([DD-11.5] P2c SP-4c, lane ctxbuild) -- THE PARSER BUILDS A_EOL FOR (?m)$,
# `$`'s twin of S1152: a multiline `$` becomes "end of subject or before a FINAL
# newline". Witness `a(?m)$` on "a\nb": libpcre2 (0,1), the plant nomatch.
SAB_ID="S1154-mline-eol-builds-eol"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness assertions"
SAB_DESC='`(?m)$` is built as A_EOL instead of the MLINE_EOL context node, so it no longer holds before an internal newline'
SAB_DOC_FIGURE='MEASURED 2026-10-20 (lane ctxbuild validation, solo mech row on the Linux dev box): corpus:509fail/70736pass,asrt:1fail/56pass -- DETECTED'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='        if (cx->mods->multiline) return mline_ctx(cx, CTXFN_MLINE_EOL, apos);'
SAB_AFTER='        (void)0;   /* SABOTAGE S1154: (?m)$ builds A_EOL */'
