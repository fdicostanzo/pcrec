#!/usr/bin/env bash
# S1195 ([DD-11.5] P2e, lane ctxp2e) -- THE END MARK'S TAIL REFUSES `\z`:
# `eol_tail_plain` answers false for the end pin, so `\Z`'s definition row
# `(?=\n?\z)` is no plain tail, `pcrec_eol_tail` answers NULL and D164 B3's
# `tagged` form is never built (ctx_span N-3: the end-mark lowering's tagged
# form reads `\z`). Answer-identical; the detector is the end-mark checks'
# form census. One of the 8 STILL-SPECIAL sites of ctx_span.md §4.6
# (definitions.c eol_tail_plain).
SAB_ID="S1195-eol-tail-rejects-end-pin"
SAB_FILE="src/parse/definitions.c"
SAB_SUITES="endmark"
SAB_DESC='eol_tail_plain refuses the end pin \z inside \Z'\''s definition row'
SAB_DOC_FIGURE='OWED (lane ctxp2e): reach measured by hand, see docs/dev/lanes/ctxp2e_report.md §5'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='        case CTX_PIN_END:
            return true;
        case CTX_PIN_START:'
SAB_AFTER='        case CTX_PIN_END:
            return false;   /* SABOTAGE S1195 */
        case CTX_PIN_START:'
