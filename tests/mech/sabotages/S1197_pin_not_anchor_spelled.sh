#!/usr/bin/env bash
# S1197 ([DD-11.5] P2e, lane ctxp2e) -- A SUBJECT PIN IS NOT SPELLED AS AN
# ANCHOR: `pcrec_ast_pin` leaves `u.ctx.anchor` false, so `pcrec_is_bare_anchor`
# answers false for `^`/`\A`/`\z` and the bare-quantified rejection lets `\A*`
# and `\z+` compile, where libpcre2 refuses them (error 109). The
# corpus's perr cells (tests/assertions/d27/syntax_errors.rxt) are the
# detector; the reject table does not carry these spellings (0 failed).
SAB_ID="S1197-pin-not-anchor-spelled"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/assertions/d27/syntax_errors.rxt"
SAB_DESC='pcrec_ast_pin builds the subject pins without the anchor spelling'
SAB_DOC_FIGURE='OWED (lane ctxp2e): by hand 2026-10-20, tests/assertions/d27/syntax_errors.rxt 10 failed / 27 passed (the \A*/\z+ perr cells compile); the reject table reads 0 failed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    Ast *a = pcrec_ast_ctx(cx, NULL, 0, fn);
    a->u.ctx.anchor = true;'
SAB_AFTER='    Ast *a = pcrec_ast_ctx(cx, NULL, 0, fn);   /* SABOTAGE S1197 */'
