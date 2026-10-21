#!/usr/bin/env bash
# S1193 ([DD-11.5] P2e, lane ctxp2e) -- THE END PIN READS `^`/`\A` AS `\z`:
# `ew_walk_marked`'s class switch answers EW_Z for the start pin, so a pattern
# that ends in `^` claims every match ends at the subject end and the end
# window starts the search at `n - W`: `^` on "ab" is (0,0) in libpcre2,
# nomatch (or a late match) under the plant. One of the 8 STILL-SPECIAL sites
# of ctx_span.md §4.6 (endwin.c EW_Z).
SAB_ID="S1193-endwin-start-pin-pins-end"
SAB_FILE="src/facts/endwin.c"
SAB_SUITES="harness assertions"
SAB_DESC='the end-pin walk answers EW_Z for the start pin ^/\A'
SAB_DOC_FIGURE='OWED (lane ctxp2e): reach measured by hand, see docs/dev/lanes/ctxp2e_report.md §5'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            case CTX_PIN_END:
                return EW_Z;
            case CTX_PIN_START:'
SAB_AFTER='            case CTX_PIN_END:
            case CTX_PIN_START:   /* SABOTAGE S1193 */
                return EW_Z;'
