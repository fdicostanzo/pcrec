#!/usr/bin/env bash
# S626 ([DEC-FALLBACK] B1, lane decfbB1) -- the `attrib` record names the
# wrong [SEL-1] row as the source of an overflowed-* token (`sel1-collapse`
# for `sel1-drop` and back), so B5's backward attribution walk would be held
# to the wrong fired row.
# Trace build only; the default build is untouched.
# Detector (arm fallbacktable): tests/codegen/run_fallback_table.sh (a)'s
# att-ovfdfa / att-ovfpf records.
SAB_ID='S626-attrib-trace-sel1-source-swapped'
SAB_FILE='src/opt/select_engine.c'
SAB_SUITES='fallbacktable'
SAB_DESC="the attrib record names the FIRST fired row instead of the one whose cell gave the token: sel1-collapse where sel1-drop gave the overflowed-* token (trace build only)"
SAB_DOC_FIGURE='Read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S626.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# [DEC-FALLBACK] B5 (lane decfbB5, 2026-10-08) RE-AIMED, INTENT RE-VERIFIED.
# The record's token-to-row derivation is deleted: since B5 it prints the
# attribution walk's own source, the fired row whose cell gave the token.
# The claim, "the record names the wrong [SEL-1] row", moves to that index:
# the plant names the FIRST fired row instead of the giving one, so on
# `sel1-collapse > sel1-drop` (W_OVF, OVFPF) the record names sel1-collapse
# for sel1-drop's ROLE cell. fbt (a)'s att-ovfdfa / att-ovfpf detect it.
SAB_BEFORE='    const char *from = src >= ESEL_FROM_ROW    ? pcrec_fit_cells_row_name(cx->fit_seq[src - ESEL_FROM_ROW])'
SAB_AFTER='    const char *from = src >= ESEL_FROM_ROW    ? pcrec_fit_cells_row_name(cx->fit_seq[0])   /* SABOTAGE S626 */'
