#!/usr/bin/env bash
# S632 ([DEC-FALLBACK] B2, lane decfbB2) -- drop-premul's on mask is widened to the overflow label, so a --engine=dfa overflow takes the premul drop instead of refusing.
# S-F7 (the on mask). Detector at B2: the oracle's arrival check on --engine=dfa (?:ab){0,16000} (fbt (a) seq-refovf, (d) or-refovf); from B3 an extra drop-premul record.
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S632-t1-drop-premul-on-overflow'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="drop-premul's on mask is widened to the overflow label, so a --engine=dfa overflow takes the premul drop instead of refusing"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S632. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .applies = fit_premul_applies, .act = FIT_DROP_PREMUL, .on = FIT_L_SIZE,'
SAB_AFTER='      .applies = fit_premul_applies, .act = FIT_DROP_PREMUL, .on = FIT_L_SIZE | FIT_L_OVERFLOW,   /* SABOTAGE S632 */'
