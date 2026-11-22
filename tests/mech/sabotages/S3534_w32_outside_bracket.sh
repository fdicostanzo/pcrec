#!/usr/bin/env bash
# S3534 -- C18 control (2) (block_span.md §10.2 [R-9], R-47 unit U4): the level function __w32 has its head written OUTSIDE the SIMD bracket. The text is unchanged (the bracket writes no text) and the answers are right; only the count of guarded bytes the sink keeps falls short of the bytes the artifact inserts. Rejected by C18's leg (c), the byte count (inserted bytes != the artifact's guarded-bytes stamp), never by compiling.
SAB_ID='S3534-w32-outside-bracket'
SAB_FILE='memfn/src/window.c'
SAB_SUITES='simdfloor'
SAB_DESC='the level function'\''s head line is written outside the SIMD bracket, so the guarded-bytes stamp undercounts the inserted text; leg (c)'\''s byte count must red'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3534. docs/dev/lanes/bsu4p_report.md carries the lane run.'
SAB_REACH='"$PCREC" --features all -fmemfn-simd=x86-64-v3 -p rx -o - --pattern "[0-9a-f]{17}"'
SAB_REACH_EXPECT='static inline __attribute__((always_inline)) int rx_mf1_vs0__w32(const unsigned char *rx_mf1_s, size_t rx_mf1_c)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    vs_head(o, "always_inline", fn, rc->S, rc->C);'
SAB_AFTER='    o->simd_close(o->u); vs_head(o, "always_inline", fn, rc->S, rc->C); o->simd_open(o->u, LV_X86_W32);   /* SABOTAGE S3534 */'
