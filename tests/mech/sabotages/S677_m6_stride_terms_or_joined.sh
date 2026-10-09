#!/usr/bin/env bash
# S677 ([MEMFN] M6, lane m6) -- THE STRIDED TERMS DISJOINED.
# A strided ADVANCE holds while EVERY term holds at its position (memfn.h's
# strided ADVANCE): the plant joins the members with `||`. The VM's strided
# loop then consumes any block with one matching byte.
SAB_ID="S677-m6-stride-terms-or-joined"
SAB_FILE="memfn/src/generic.c"
SAB_SUITES="harness memfnarms"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='the kit joins a strided ADVANCE'"'"'s per-position member tests with || instead of &&, so the VM'"'"'s strided span loop advances when ANY position of the block matches'
SAB_DOC_FIGURE="HAND-MEASURED by lane m6 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m6_report.md section 6): harness tests/possessify/possessify.rxt 223 failed / 3314 passed; memfnarms 14 failed / 324 passed (twelve pins/freezes move; check 13 fails to BUILD: -Werror=parentheses on the || within &&). The matrix figure is owed at the slot."
SAB_REACH='"$PCREC" -p rx --engine=vm -o - --pattern "(?:ab)+c"'
SAB_REACH_EXPECT='while ((rx_span_cursor + 2 <= subject_length) && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98)) {'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (t) kb_puts(&test, " && ");'
SAB_AFTER='        if (t) kb_puts(&test, " || ");  /* SABOTAGE S677 */'
