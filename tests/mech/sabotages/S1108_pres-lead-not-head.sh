#!/usr/bin/env bash
# S1108 (lane b3b, [MEMFN] R17-b' B3b; r17b_prime.md rev 3 §1.4 P4's LEAD,
# KW-7's chain order) -- THE LEAD LOSES ITS PLACE IN THE CHAIN. P4 verifies
# the set's pick but no longer puts it at the HEAD, ahead of the run, so the
# chain tests it after the run, in the rest: the leading `memchr` [K82] (A)
# exists for is gone (no answer moves: the member is still tested).
# Detectors: the pre-check suite's lead cells and the kit's finder check
# (fd-P4's head link reads order 2).
SAB_ID="S1108-pres-lead-not-head"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder prechecks"
SAB_DESC="the PRES row P4 verifies the set's pick without putting it at the head of the chain, so the leading memchr in front of the run becomes a rest member tested after it"
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?:user|USER)[ \\t]*=" && grep -q "!memchr(subject + search_from, 61," "$REACH_TMP/o.c" && echo REACH-SET-LEADS'
SAB_REACH_EXPECT="REACH-SET-LEADS"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            led[i] = 1;'
SAB_AFTER='            led[i] = 0;   /* SABOTAGE S1108 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3b: see docs/dev/lanes/b3b_report.md (the solo mech run of this row)."
