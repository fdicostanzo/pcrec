#!/usr/bin/env bash
# S1191 ([DD-11.5] P2e, lane ctxp2e) -- THE EMPTY-PATH MASK READS `^`/`\A` AS
# AN END ANCHOR: `em_set`'s start-pin case marks EM_E. A nullable `^`-led
# pattern then claims its empty match lies at the subject END, the prefilter
# decline it feeds misreads where an empty match can be, and the start-pin
# empty match at offset 0 can be dismissed. One of the 8 STILL-SPECIAL sites of
# ctx_span.md §4.6 (widths.c EM_S).
SAB_ID="S1191-emptypath-start-pin-marks-end"
SAB_FILE="src/facts/widths.c"
SAB_SUITES="harness pfcollapse"
SAB_HARNESS_TARGET="tests/base/nullable_anch.rxt"
SAB_DESC='the empty-path anchor mask marks a ^/\A with EM_E instead of EM_S'
SAB_DOC_FIGURE='OWED (lane ctxp2e): by hand 2026-10-20, tests/base/nullable_anch.rxt 2 failed / 60 passed; prefilter-collapse 6 failed / 65 passed'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            case CTX_PIN_START: return em_cat(acc, 1u << EM_S);'
SAB_AFTER='            case CTX_PIN_START: return em_cat(acc, 1u << EM_E);   /* SABOTAGE S1191 */'
