#!/usr/bin/env bash
# S1639 (S-IC22; [INLINE-C] stage 1a, lane ic1a, 2026-10-26; docs/design/inline_c.md §1.8, docs/dev/lanes/ic1a_report.md) -- the PER-KIND ROW's TEXT column for the variable flips ANY -> ZERO: every text reader (`row_cwmax` in mrl.c, `rb_row_into` in req.c, `ss_row` in startset.c, possessify's text_first) reads `${v}` as matching the empty string only, so the start set of `${v}x` narrows to {x}, the maximum width collapses, and `^${v}$` stops matching any non-empty value. The text family's row read.
# Detector: tests/vars/run_vars_tests.sh (the `vars` arm). MEASURED by plant at landing: 28 of 88 corpus cases fail.
SAB_ID='S1639-kindrow-var-text-zero'
SAB_FILE='src/core/kindrow.def'
SAB_SUITES='vars'
SAB_DESC='the variable row reads TEXT ZERO: the start set, required run and widths read a variable as the empty string'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ic1a_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1639.'
SAB_REACH='"$PCREC" --features all --emit-facts -p rx --pattern "\${v}x" | grep -qP "^byte\tstart_set\tpattern\t.*\tnullable\t" && echo REACH-VAR-START-ANY'
SAB_REACH_EXPECT='REACH-VAR-START-ANY'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='KIND_ROW(A_VAR,     ANY,  OPAQUE,      NONE,   0)'
SAB_AFTER='KIND_ROW(A_VAR,     ZERO, OPAQUE,      NONE,   0)   /* SABOTAGE S1639 */'
