#!/usr/bin/env bash
# S2930 -- span_pick stage 2 unit S2c, sabotage (m) (docs/design/memfn/span_cards.md §9's S2c row;
# lane memfn-s2c). TWO FORM IDS HASHING ONE TEXT.
#
# Plant: formhash.c's entry table gives `pair` the walk's site shape and facts (a FIND over the table
# set [0-9], row pf_walk), so `pair` and `walk` render one text under two ids.
# Detector: tests/memfn/finder_check.py check B (arm memfnfinder): every entry-table instance hashes
# pairwise distinct ("form instances hash one text"); `pair`'s design row PAIR is also missed.
SAB_ID="S2930-formhash-two-ids-one-text"
SAB_FILE="memfn/src/formhash.c"
SAB_SUITES="memfnfinder"
SAB_DESC='the form-hash entry table renders two ids (pair, walk) from one site: one form under two names'
SAB_DOC_FIGURE='MEASURED by lane memfn-s2c (sub-lane fh) planted and reverted by hand; exact re-run: bash tests/mech/run_sabotage_matrix.sh S2930.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "pair",      "-",  1, MF_FH_WINDOW,  "PAIR",      "Xx",                 0, 0, MF_EMPTY_MISS,     0, NULL,        "generic",          NULL },'
SAB_AFTER='    { "pair",      "-",  1, MF_FH_FIND,    "pf_walk",   DIGITS,               0, 1, MF_EMPTY_NOP,      0, NULL,        "generic",          NULL },   /* SABOTAGE S2930 */'
