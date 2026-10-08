#!/usr/bin/env bash
# S637 ([DEC-FALLBACK] B2, lane decfbB2) -- drop-anchored's note cell is empty, so the stderr note for a dropped anchored machine would not print once the notes loop over fired rows.
# The note column (B3 makes the notes a loop over fired rows). Detector at B2: the oracle's notes check, which holds the note rows to the dropped_* flags (fbt (a)/(d), every compiling witness).
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S637-t1-drop-anchored-note-lost'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="drop-anchored's note cell is empty, so the stderr note for a dropped anchored machine would not print once the notes loop over fired rows"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S637. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .note = { "the optional anchored match-here machine",'
SAB_AFTER='      .note = { NULL, /* SABOTAGE S637 */'
