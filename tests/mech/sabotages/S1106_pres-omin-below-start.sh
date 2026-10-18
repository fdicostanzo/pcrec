#!/usr/bin/env bash
# S1106 (lane b3b, [MEMFN] R17-b' B3b; r17b_prime.md rev 3 §4.1, window_contract
# C-1, KW-10's "re-asked ranges with omin < 0") -- A PRESENCE SPAN MAY BEGIN
# BELOW THE MATCH START. `omin` is measured from the match start and is never
# negative (the verdict window is [start + omin, n), which reads nothing below
# the activation's start); the plant drops the refusal, so a span stating
# omin < 0 would be decided over a re-asked range below the start. No pcrec
# builder states one (every omin is 0 through B4), so no artifact moves: the
# detector is the kit's contract check (finder_check M: `pre-omin` refused
# naming omin).
SAB_ID="S1106-pres-omin-below-start"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the presence statement's omin >= 0 refusal is dropped, so a span beginning below the match start is accepted (a re-asked range below the activation's start; KW-10)"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (p->omin < 0) return "a presence span'"'"'s `omin` is below the match start";'
SAB_AFTER='        if (0 && p->omin < 0) return "a presence span'"'"'s `omin` is below the match start";   /* SABOTAGE S1106 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3b: see docs/dev/lanes/b3b_report.md (the solo mech run of this row)."
