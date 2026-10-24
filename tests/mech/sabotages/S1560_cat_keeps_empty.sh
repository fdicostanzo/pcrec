#!/usr/bin/env bash
# S1560 ([FLAG-SPELL], lane flagfix) -- A CONCATENATION KEEPS ITS EMPTIES.
#
# THE CLAIM: src/parse/parse.c's p_cat drops an empty that carries nothing
# from the spine it builds, so `(?i)abc` (a bare option run, which parses to
# an empty) builds the same tree as `(?i:abc)`. The plant makes the predicate
# false, so every such empty stays: the VM emits a dead label + goto for it.
# Answers cannot move (an empty matches the empty string either way), so the
# only detector is the spelling identity check's flag group, which compares
# `(?i)abc` against `(?i:ABC)` (arm `casespell`, the VM cells).
SAB_ID="S1560-cat-keeps-empty"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="casespell"
SAB_DESC="p_cat keeps an empty that carries nothing; caught by the flag group of the case-spelling identity check ((?i)abc vs (?i:ABC) on the VM)"
SAB_DOC_FIGURE="OWED: solo mech run of this row (docs/dev/lanes/flagfix_report.md)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return a->k == A_EMPTY && !a->reg;'
SAB_AFTER='    (void)a; return false;   /* SABOTAGE S1560: every empty stays in its concatenation */'
SAB_REACH='"$PCREC" -p rx --engine=vm --emit-ir --pattern "(?i)" | grep -qE "^L0[[:space:]]+label[[:space:]]+empty$" && ! "$PCREC" -p rx --engine=vm --emit-ir --pattern "(?i)abc" | grep -qE "[[:space:]]empty$" && echo REACH-BARE-RUN-DROPPED'
SAB_REACH_EXPECT="REACH-BARE-RUN-DROPPED"
