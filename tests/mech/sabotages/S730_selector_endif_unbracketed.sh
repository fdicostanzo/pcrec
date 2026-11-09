#!/usr/bin/env bash
# S730 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- a selector byte left unbracketed (§R4.9.8 C18 row): C18 leg (c) holds the inserted bytes equal to SIMD_GUARDED_BYTES. Re-aimed at unit U2 (lane u2): the selector has no `#endif` now; its one call line naming a rung is closed out of the bracket instead. Detects once pcrec states a target (unit U3): on this branch alone simdfloor renders no SIMD.
SAB_ID='S730-selector-endif-unbracketed'
SAB_FILE='memfn/src/ofsskip.c'
SAB_SUITES='simdfloor'
SAB_DESC='the selector'\''s call line naming a rung is written outside the simd bracket, so SIMD_GUARDED_BYTES undercounts'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S730. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'        o->simd_open(o->u, (int)rung[0]->decl->level);\n        if (fn_call_line(art, h, p, names[0], o)) return -1;\n        o->simd_close(o->u);'
SAB_AFTER=$'        o->simd_open(o->u, (int)rung[0]->decl->level);\n        o->simd_close(o->u);   /* SABOTAGE S730 */\n        if (fn_call_line(art, h, p, names[0], o)) return -1;'
