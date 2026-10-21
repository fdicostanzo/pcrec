#!/usr/bin/env bash
# S1188 ([DD-11.5] P2e, lane ctxp2e) -- THE START-ANCHOR FACT READS THE END
# PIN AS THE START PIN: `sa_walk`'s class switch answers SA_BOT for `\z`. The
# artifact then attempts at offset 0 only, and every match of a `\z`-led or
# `\z`-only start is lost: `a\z` on "ba" is (1,2) in libpcre2, nomatch under
# the plant. One of the 8 STILL-SPECIAL sites of ctx_span.md §4.6 (startanch).
SAB_ID="S1188-startanch-end-pin-anchors"
SAB_FILE="src/facts/startanch.c"
SAB_SUITES="harness assertions"
SAB_DESC='the start-anchor walk answers SA_BOT for the end pin \z'
SAB_DOC_FIGURE='OWED (lane ctxp2e): reach measured by hand, see docs/dev/lanes/ctxp2e_report.md §5'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            case CTX_PIN_START:
                return acc | SA_BOT;
            case CTX_PIN_END:
            case CTX_CONTEXT:'
SAB_AFTER='            case CTX_PIN_START:
            case CTX_PIN_END:   /* SABOTAGE S1188 */
                return acc | SA_BOT;
            case CTX_CONTEXT:'
