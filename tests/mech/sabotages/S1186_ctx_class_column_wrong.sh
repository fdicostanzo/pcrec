#!/usr/bin/env bash
# S1186 ([DD-11.5] P2e, lane ctxp2e) -- THE CLASS COLUMN DISAGREES WITH ITS
# GRID: ctxfn.def writes SUBJECT_END's class as CONTEXT. The class is derived
# from the grid (internal.h's CTXFN_CLASS_OF) and the written column is a
# statement the build checks against it (one _Static_assert per row, HEX's
# shape), so the plant must not build. CK-8's class half
# (tests/assertions/ctxfn_table_check.py) is the second, libpcre2-side detector
# of the same edit; its failing direction is measured on a planted copy of the
# .def (the build refuses the tree first).
SAB_ID="S1186-ctx-class-column-wrong"
SAB_FILE="src/core/ctxfn.def"
SAB_SUITES="harness"
SAB_DESC='ctxfn.def writes the \z row'\''s class as CONTEXT where its grid derives PIN_END'
SAB_DOC_FIGURE='OWED (lane ctxp2e): by hand 2026-10-20, the build refuses (static assertion: SUBJECT_END written CONTEXT, grid derives PIN_END)'
SAB_EXPECT='BUILD-REFUSED'
SAB_COUNT='1'
SAB_BEFORE='          PIN_END, VMCTX_END, NULL, false,'
SAB_AFTER='          CONTEXT, VMCTX_END, NULL, false,   /* SABOTAGE S1186 */'
