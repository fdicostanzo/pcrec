#!/usr/bin/env bash
# S1189 ([DD-11.5] P2e, lane ctxp2e) -- THE SPLIT DERIVATION NO LONGER KILLS
# `^`/`\A`: q_rewrite's start-pin case keeps the node, so Q carries a floor
# anchor outside any lookbehind. G5's independent walk (`qp_walk`, a different
# function reading the same class) counts it and the derivation DECLINES the
# part, so the compound row stops admitting. One of the 8 STILL-SPECIAL sites
# of ctx_span.md §4.6 (derive.c:225).
SAB_ID="S1189-derive-keeps-start-pin"
SAB_FILE="src/opt/derive.c"
SAB_SUITES="compound"
SAB_DESC='the [MATCH-SPLIT] derivation keeps every ^/\A in Q instead of killing it'
SAB_DOC_FIGURE='OWED (lane ctxp2e): reach measured by hand, see docs/dev/lanes/ctxp2e_report.md §5'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            if (lb) return (QRes){ a, false, false };
            q->killed_bol++;'
SAB_AFTER='            return (QRes){ a, false, false };   /* SABOTAGE S1189 */
            q->killed_bol++;'
