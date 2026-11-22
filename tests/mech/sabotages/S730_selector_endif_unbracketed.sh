#!/usr/bin/env bash
# S730 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- a selector byte left unbracketed (§R4.9.8 C18 row): C18 leg (c) holds the inserted bytes equal to SIMD_GUARDED_BYTES. Re-aimed at unit U2 (lane u2): the selector has no `#endif` now; its one call line naming a rung is closed out of the bracket instead. Detects once pcrec states a target (unit U3): on this branch alone simdfloor renders no SIMD.
# Re-aimed by lane bsu2 (R-47 U2, block_span.md §10.2, review r69 R-4): fn_selector's lines moved into the kit-wide selector writer kit_selector (ofsskip.c), which every selector (ofsskip's FUNC, window.c's vector span) is written by; same intent.
SAB_ID='S730-selector-endif-unbracketed'
SAB_FILE='memfn/src/ofsskip.c'
SAB_SUITES='simdfloor'
SAB_DESC='the selector'\''s call line naming a rung is written outside the simd bracket, so SIMD_GUARDED_BYTES undercounts'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S730. docs/dev/lanes/r13_report.md carries the lane run.'
# REACH (lane bsu2, U2): the ofsskip witness, a FUNC selector with a SIMD rung. The V selector shares the
# writer but has no rung at U2 (`__body` only, top NULL), so it does not reach this anchor until U3's __w32.
# REACH (lane bsu3, U3, owed since U2): the V witness too, now that the vector span's selector has a
# rung (`__w32` at the 32-byte target): the writer is shared, so the plant reaches both selectors.
SAB_REACH='"$PCREC" --features all -fmemfn-simd=x86-64-v3 -p rx -o - --pattern "(?i)cat"; "$PCREC" --features all -fmemfn-simd=x86-64-v3 -p rx -o - --pattern "[0-9a-f]{17}"'
SAB_REACH_EXPECT=$'    return rx_mf1_ofsskip__w32(subject, n, pos);\n    return rx_mf1_vs0__w32(rx_mf1_s, rx_mf1_c);'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'        o->simd_open(o->u, level);\n        if (call(ctx, top, o)) return -1;\n        o->simd_close(o->u);'
SAB_AFTER=$'        o->simd_open(o->u, level);\n        o->simd_close(o->u);   /* SABOTAGE S730 */\n        if (call(ctx, top, o)) return -1;'
