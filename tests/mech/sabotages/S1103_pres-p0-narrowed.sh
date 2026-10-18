#!/usr/bin/env bash
# S1103 (lane b3b, [MEMFN] R17-b' B3b; r17b_prime.md rev 3 §1.4, §8.3 SW-1,
# KW-6's APPLICABILITY rule) -- A REQUIRED SPAN NARROWED BY THE PICK. The PRES
# row P0 decides every span the route with no DFA scan in front states
# REQUIRED (K65's whole set, K66's whole run: the call's only linear no-match
# proof); the plant gives P0's spans P3's narrowing (only the set's pick, and
# the run's window), so on that route a subject lacking another member, or
# holding the window but not the whole run, gives up on the step budget where
# the answer is NOMATCH. Reaches the NON-DFA route by construction (P0 holds
# nowhere else). Detectors: the harness on K65's file (answers) and the kit's
# own finder check (fd-P0's link reads the pick's, not P0's).
SAB_ID="S1103-pres-p0-narrowed"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder harness"
SAB_HARNESS_TARGET="tests/base/k65_precheck_whole_set.rxt"
SAB_DESC="the routed PRES row P0 (a REQUIRED presence span, the no-DFA route) takes P3's narrowing: only the set's pick and the run's window are verified, so a pick-dependent NOMATCH turns into a step give-up (K65/K66, SW-1)"
SAB_REACH='"$PCREC" --features all -e byte -p rx -o "$REACH_TMP/o.c" --pattern "(x?)([a-z]+)+Z.@\\1" && grep -q "^#define RX_VM_PREFILTER \"none\"" "$REACH_TMP/o.c" && grep -q "static const unsigned char rq_set\[\] = { 64 };" "$REACH_TMP/o.c" && echo REACH-P0-WHOLE-SET'
SAB_REACH_EXPECT="REACH-P0-WHOLE-SET"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (!strcmp(t->id, "P3")) {'
SAB_AFTER='        if (!strcmp(t->id, "P3") || !strcmp(t->id, "P0")) {   /* SABOTAGE S1103 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3b: see docs/dev/lanes/b3b_report.md (the solo mech run of this row)."
