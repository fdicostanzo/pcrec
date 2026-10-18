#!/usr/bin/env bash
# S1101 (lane b3a, [MEMFN] R17-b' B3a) -- a stated presence span leaves span_class UNSTATED: the kit refuses the site (presence_check); caught by the witness compiles
SAB_ID="S1101-pspan-class-unstated"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="candoracle"
SAB_DESC="a stated presence span leaves span_class UNSTATED: the kit refuses the site (presence_check); caught by the witness compiles"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        p[i].span_class = MF_SPAN_PRESENCE;'
SAB_AFTER='        (void)0;   /* SABOTAGE S1101 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3afix: see docs/dev/lanes/b3a_report.md §9 (the solo mech run of this row, candoracle:59fail/79pass DETECTED at ebfb5a88a)."
