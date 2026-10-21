#!/usr/bin/env bash
# S1187 ([DD-11.5] P2e, lane ctxp2e) -- THE CLASS DERIVATION LOSES THE END
# PIN: CTXFN_CLASS_OF answers CONTEXT for every function that is not the start
# pin, so `\z` would read as a plain context node at every analysis (no end
# pin, no window, no transparency, no tail). The written column still says
# PIN_END, so the per-row _Static_assert refuses the build: the derivation and
# the column check each other.
SAB_ID="S1187-ctx-class-derivation-drops-end-pin"
SAB_FILE="src/core/internal.h"
SAB_SUITES="harness"
SAB_DESC='CTXFN_CLASS_OF never answers CTX_PIN_END'
SAB_DOC_FIGURE='OWED (lane ctxp2e): by hand 2026-10-20, the build refuses (static assertion: SUBJECT_END written PIN_END, derived CONTEXT)'
SAB_EXPECT='BUILD-REFUSED'
SAB_COUNT='1'
SAB_BEFORE='     : (fn) == CTXFN_GRID_PIN_END ? CTX_PIN_END : CTX_CONTEXT)'
SAB_AFTER='     : CTX_CONTEXT)   /* SABOTAGE S1187 */'
