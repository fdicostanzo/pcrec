#!/usr/bin/env bash
# S1190 ([DD-11.5] P2e, lane ctxp2e) -- G5'S COUNT IS BLIND TO THE START PIN:
# `qp_walk` stops counting `^`/`\A` outside a lookbehind, so the derivation's
# own check reads "no surviving floor anchor" on every Q and the KILLED count
# (P's minus Q's) reads 0 where the rewrite killed some. One of the 8
# STILL-SPECIAL sites of ctx_span.md §4.6 (derive.c:291).
SAB_ID="S1190-derive-check-blind-to-start-pin"
SAB_FILE="src/opt/derive.c"
SAB_SUITES="compound"
SAB_DESC='the derivation'\''s G5 walk never counts a ^/\A'
SAB_DOC_FIGURE='OWED (lane ctxp2e): by hand 2026-10-20, test-compound red (fixtures split-f/split-np/split-q no longer admitted)'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            case CTX_PIN_START: if (!lb) p->bol_out++; return;'
SAB_AFTER='            case CTX_PIN_START: return;   /* SABOTAGE S1190 */'
