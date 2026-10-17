#!/usr/bin/env bash
# SK-B3A-9 (PLACEHOLDER id; lane b3a, [MEMFN] R17-b' B3a) -- a stated presence span leaves span_class UNSTATED: the kit refuses the site (presence_check); caught by the witness compiles
SAB_ID="SK-B3A-9-pspan-class-unstated"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="candoracle"
SAB_DESC="a stated presence span leaves span_class UNSTATED: the kit refuses the site (presence_check); caught by the witness compiles"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        p[i].span_class = MF_SPAN_PRESENCE;'
SAB_AFTER='        (void)0;   /* SABOTAGE SK-B3A-9 */'
