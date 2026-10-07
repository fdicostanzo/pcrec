#!/usr/bin/env bash
# S572 ([MEMFN] M1b, lane m1b) -- THE PROLOGUE NEVER DECLARES THE VM'S HELPERS.
#
# A VM body is written BEFORE the prologue, so its literal-run compares only
# RECORD the word widths they load on the attempt's art, and the prologue's
# flush (`pcrec_memfn_flush_helpers` in pcrec_emit_prologue, the kit's
# mf_flush_helpers) declares them (integration.md §14.8, §R4.8.1 item 2). The
# plant deletes that flush, so every VM artifact with a word compare calls an
# undeclared `rx_w<W>`: the artifact no longer compiles. Detector:
# tests/codegen/runcmp_check.py (helpers declared for exactly the widths
# used, ahead of use; every witness compiles under -Werror).
SAB_ID="S572-prologue-helpers-not-flushed"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="pcrec_emit_prologue no longer flushes the kit's pending word-load helpers, so a VM artifact's run compares call rx_w<W> functions it never declares"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/m1b_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S572."
SAB_REACH='"$PCREC" --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "xyz(a|ab)c" && grep -qF "static inline uint16_t rx_w2(const void *p)" "$REACH_TMP/o.c" && grep -qF "rx_w2(subject + scan_position + 1) == rx_w2(\"yz\")" "$REACH_TMP/o.c" && echo REACH-VM-HELPER-DECLARED'
SAB_REACH_EXPECT="REACH-VM-HELPER-DECLARED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_memfn_flush_helpers(cx, c);'
SAB_AFTER='    /* SABOTAGE S572: the prologue declares no word-load helper */'
