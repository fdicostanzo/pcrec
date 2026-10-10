#!/usr/bin/env bash
# S687 ([MEMFN] R4e'.0, lane r4e0) -- THE EMPTY PREFIX SLOT RENDERS TEXT.
#
# WHAT IT BREAKS. fn_rows[]' PREFIX slot (the guarded per-level helpers
# beside the body, D155) is BORN EMPTY: an empty slot renders zero bytes, so
# R4e'.0 moves no byte pcrec emits (integration.md §R4.9.2.1 item 2). The
# plant makes the seam write a separator for the PREFIX slot whether or not a
# row was chosen (the shape of a seam that brackets the slot unconditionally),
# so every FUNC part of every offset-skip and pre-check site gains a line.
# Answer-identical by construction (a blank line at file scope).
#
# WHERE IT IS SEEN. C5's pins of the offset-skip and pre-check fixtures (arm
# memfnarms): every FUNC part's rendering moves by one byte.
SAB_ID="S687-fn-prefix-rendered-when-empty"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="memfnarms"
SAB_DESC="the seam writes text for fn_rows[]' PREFIX slot when no PREFIX row is chosen, so the empty slot moves every FUNC part by a byte"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4e0 2026-10-09 (one mech row, solo): see docs/dev/lanes/r4e0_report.md §4. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S687."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "abc[0-9]+xyz"'
SAB_REACH_EXPECT='static inline size_t rx_ofsskip(const unsigned char *subject, size_t n, size_t pos)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# Re-aimed by lane r13 (R-13, 2026-10-09): its anchor moved with the R4e' batch 1 seam
# (kit_walk's per-row step / fn_rows[]'s decl column / the seam's level blocks); same intent.
SAB_BEFORE='    for (unsigned j = nr; j-- > 0;)'
SAB_AFTER='    if (!prefix) o->puts(o->u, "\n");   /* SABOTAGE S687 */
    for (unsigned j = nr; j-- > 0;)'
