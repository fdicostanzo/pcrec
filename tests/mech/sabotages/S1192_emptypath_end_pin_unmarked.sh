#!/usr/bin/env bash
# S1192 ([DD-11.5] P2e, lane ctxp2e) -- THE EMPTY-PATH MASK LOSES `\z`:
# `em_set`'s end-pin case answers mask 0, so an empty path through `\z` reads
# as unanchored. One of the 8 STILL-SPECIAL sites of ctx_span.md §4.6
# (widths.c EM_E).
SAB_ID="S1192-emptypath-end-pin-unmarked"
SAB_FILE="src/facts/widths.c"
SAB_SUITES="pfcollapse"
SAB_DESC='the empty-path anchor mask gives \z mask 0 instead of EM_E'
SAB_DOC_FIGURE='OWED (lane ctxp2e): by hand 2026-10-20, prefilter-collapse 1 failed / 70 passed (tests/base/nullable_anch.rxt reads 0 failed: answer-identical)'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            case CTX_PIN_END:   return em_cat(acc, 1u << EM_E);'
SAB_AFTER='            case CTX_PIN_END:   return acc;   /* SABOTAGE S1192 */'
