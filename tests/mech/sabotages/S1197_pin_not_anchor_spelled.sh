#!/usr/bin/env bash
# S1197 ([DD-11.5] P2e, lane ctxp2e) -- A SUBJECT PIN IS NOT SPELLED AS AN
# ANCHOR: `pcrec_ast_pin` leaves `u.ctx.anchor` false, so `pcrec_is_bare_anchor`
# answers false for `^`/`\A`/`\z` and the bare-quantified rejection lets `\A*`
# and `\z+` compile, where libpcre2 refuses them (error 109). The reject
# table is the detector.
SAB_ID="S1197-pin-not-anchor-spelled"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="reject"
SAB_DESC='pcrec_ast_pin builds the subject pins without the anchor spelling'
SAB_DOC_FIGURE='OWED (lane ctxp2e): reach measured by hand, see docs/dev/lanes/ctxp2e_report.md §5'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    Ast *a = pcrec_ast_ctx(cx, NULL, 0, fn);
    a->u.ctx.anchor = true;'
SAB_AFTER='    Ast *a = pcrec_ast_ctx(cx, NULL, 0, fn);   /* SABOTAGE S1197 */'
