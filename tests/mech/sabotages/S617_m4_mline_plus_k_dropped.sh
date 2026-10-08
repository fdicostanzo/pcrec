#!/usr/bin/env bash
# S617 ([MEMFN] M4, lane m4) -- THE KIT'S `+ k` STORE IS DROPPED.
#
# WHAT IT BREAKS. MLINE's `(?m)^` skip is a FIND whose one term sits one byte
# BELOW the candidate (the predecessor `\n`, offset -1). The kit's row
# pf_memchr_back (memfn/src/pffind.c) searches the term's byte and stores
# the hit PLUS the term's offset back: `start = (size_t)(q - subject) + 1;`.
# The plant drops the `+ k`, so the stored position is the newline itself,
# one short of the candidate.
#
# WHY NO ANSWER MOVES ON pcrec's ONE CUSTOMER, AND WHERE IT IS SEEN. In
# emit_attempt the attempt at the newline's own position enters a dead seeded
# state (its predecessor is not a newline), records nothing and the loop's
# `start++` lands on the true candidate: a slower artifact, not a wrong one
# (hand-checked by lane m4, report §6). The defect is the KIT's contract
# (MF_OP_FIND's result), so the detector is the kit's: C5's pin of the
# `pf-memchr-back` fixture moves, and check 9 runs that fixture's text on
# fixed subjects against a byte loop ("a\n" from 0 must answer 2, not 1).
# Arm memfnarms (tests/memfn/run_arm_pins.sh).
SAB_ID="S617-m4-mline-plus-k-dropped"
SAB_FILE="memfn/src/pffind.c"
SAB_SUITES="memfnarms"
SAB_DESC="the kit's pf_memchr_back row drops the '+ k' of its store, so a FIND whose term sits below its candidate returns the predecessor's position (MLINE: the newline, not the line start)"
SAB_DOC_FIGURE="HAND-MEASURED by lane m4 (plant applied, tree rebuilt): run_arm_pins.sh 2 failed / 237 passed (the pf-memchr-back pin moved, 178 -> 174 bytes; check 9: the row answers c - 1 on 7 of 10 subjects); the corpus is GREEN under it (tests/assertions/multiline.rxt + gpos.rxt 3655/0, d27 multiline/composition + utf8 k73 + litscan handoff 2545/0, run_mline_diff.sh 4/0), as the header argues; see docs/dev/lanes/m4_report.md §6. The matrix's own figure is owed at the slot."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "(?m)^abc"'
SAB_REACH_EXPECT='const void *q = memchr(subject + start, 10, subject_length - start);
start = (size_t)((const unsigned char *)q - subject) + 1;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (k) kit_out(o, " + %d", (int)k);'
SAB_AFTER='        (void)k;  /* SABOTAGE S617: the + k store dropped */'
