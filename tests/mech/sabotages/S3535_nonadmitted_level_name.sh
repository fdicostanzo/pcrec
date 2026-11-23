#!/usr/bin/env bash
# S3535 -- C18 control (3) (block_span.md §10.2, R-47 unit U4): the vector span names a level its target does not admit (the helper and the selector's callee carry the width 64 where the table admits only 32). The text is self-consistent and compiles; the EXCLUSIVITY lint, which now sees the block helper's name (the HELPER regex's name form), reads a helper of no admitted level.
SAB_ID='S3535-nonadmitted-level-name'
SAB_FILE='memfn/src/window.c'
SAB_SUITES='simdfloor'
SAB_DESC='the vector span'\''s level helpers are named for a level the target does not admit, so the exclusivity lint must red'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3535. docs/dev/lanes/bsu4p_report.md carries the lane run.'
SAB_REACH='"$PCREC" --features all -fmemfn-simd=x86-64-v3 -p rx -o - --pattern "[0-9a-f]{17}"'
SAB_REACH_EXPECT='static inline __attribute__((always_inline)) int rx_mf1_vs0__w32(const unsigned char *rx_mf1_s, size_t rx_mf1_c)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        const char *stamp = kit_level(LV_X86_W32)->stamp;'
SAB_AFTER='        const char *stamp = "w64";   /* SABOTAGE S3535 */'
