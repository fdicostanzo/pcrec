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
SAB_DESC="the attrib record names sel1-collapse where sel1-drop gave the overflowed-* token, and back (trace build only)"
SAB_DOC_FIGURE='Read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S626.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        : cr == CR_NONE                                     ? "sel1-drop"
        :                                                     "sel1-collapse";'
SAB_AFTER='        : cr == CR_NONE                                     ? "sel1-collapse"   /* SABOTAGE S626 */
        :                                                     "sel1-drop";'
