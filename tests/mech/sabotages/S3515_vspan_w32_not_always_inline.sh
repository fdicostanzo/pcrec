#!/usr/bin/env bash
# S3515 ([MEMFN] R-47 unit U3, lane bsu3, 2026-11-21) -- C18's -O0 rule, control (1) (docs/design/memfn/block_span.md §10.2 "The C18 amendment"): the vector span's level helper `<p>_mf<h>_vs<j>__w32` loses `always_inline`. Answer-identical and invisible at -O2 (gcc inlines the static anyway). TWO legs of C18 reject it: the V head lint (review r75 CHECKS-8) reads the same head, and the -O0 rule (the selector's own head says always_inline, so no symbol of its family may be defined at -O0, here `__w32` is, and its caller holds none of the level block's byte-shuffle instructions; drilled on three witnesses, §16 item 10). So this row proves the SUITE, not the -O0 rule alone: that rule's own control is the in-script V_O0_CONTROL, whose row is S3516 (r76 CHECKS-1).
SAB_ID='S3515-vspan-w32-not-always-inline'
SAB_FILE='memfn/src/window.c'
SAB_SUITES='simdfloor'
SAB_DESC='the vector span'\''s w32 level helper is written without always_inline, so at -O0 it is an out-of-line symbol and the vector test is not inlined into its caller'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3515. docs/dev/lanes/bsu3_report.md carries the lane run.'
# REACH: the C18 NAMED-class witness the design drills (k 16, B 16), its __w32 head as the
# clean tree writes it at the 32-byte target.
SAB_REACH='"$PCREC" --features all -fmemfn-simd=x86-64-v3 -p rx -o - --pattern "[0-9a-f]{17}"'
SAB_REACH_EXPECT='static inline __attribute__((always_inline)) int rx_mf1_vs0__w32(const unsigned char *rx_mf1_s, size_t rx_mf1_c)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    vs_head(o, "always_inline", fn, rc->S, rc->C);'
SAB_AFTER='    vs_head(o, "unused", fn, rc->S, rc->C);   /* SABOTAGE S3515 */'
