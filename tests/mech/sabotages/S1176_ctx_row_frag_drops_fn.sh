#!/usr/bin/env bash
# S1176 ([DD-11.5] P2d, lane ctxp2d; RE-AIMED at P2e, lane ctxp2e) -- THE
# NFA DROPS THE ROW OF EVERY CONTEXT NODE THAT READS NO MEMBERSHIP: the A_CTX
# lowering writes `ctxfn` 0 (the function no position passes) for `^`/`\A`/`\z`.
# P2d planted `frag_ctx_row`, the one-state fragment the two retired AST kinds
# lowered through; P2e deleted it (the pins are A_CTX nodes and take the A_CTX
# arm), so the plant moves there, keeping its intent: every DFA-routed pin dies
# in the closure and `pcrec_nfa_has_bot` stops seeing `^`. `^a` on "a" is
# (0,1) in libpcre2, nomatch under the plant; the VM is untouched.
SAB_ID="S1176-ctx-row-frag-drops-fn"
SAB_FILE="src/ir/nfa.c"
SAB_SUITES="harness assertions"
SAB_DESC='the NFA lowers ^/\A/\z (the context rows that read no membership) to an N_CTX state with truth function 0'
SAB_DOC_FIGURE='OWED (lane ctxp2e): reach measured by hand, see docs/dev/lanes/ctxp2e_report.md §5'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='        st->ctxfn = a->u.ctx.fn;'
SAB_AFTER='        st->ctxfn = ctxfn_reads_membership(a->u.ctx.fn) ? a->u.ctx.fn : 0;   /* SABOTAGE S1176 */'
