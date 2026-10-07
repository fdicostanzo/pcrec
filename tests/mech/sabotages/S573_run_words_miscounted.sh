#!/usr/bin/env bash
# S573 ([MEMFN] M1b, lane m1b) -- RUN_WORDS COUNTS EACH WORDS COMPARE TWICE.
#
# `<PREFIX>_RUN_WORDS` is the kit's stamp since M1b (integration.md §R4.8.1
# item 1; docs/spec/tuning.md §2.38): the number of run compares the
# artifact's text wrote through the `words` form, counted on the art by the
# words writer and written by mf_stamps through the sink's unquoted
# `stamp_int`. The plant counts each compare twice, so the stamp disagrees
# with the text on every artifact that has a word compare. Detector:
# tests/codegen/runcmp_check.py ("RX_RUN_WORDS equals the word compares in
# the text").
SAB_ID="S573-run-words-miscounted"
SAB_FILE="memfn/src/runcmp.c"
SAB_SUITES="codegen"
SAB_DESC="the kit's words writer counts each compare twice, so RUN_WORDS reads double the word compares the artifact carries"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/m1b_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S573."
SAB_REACH='"$PCREC" --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "xyz(a|ab)c" && grep -q "^#define RX_RUN_WORDS 1$" "$REACH_TMP/o.c" && echo REACH-RUN-WORDS-ONE'
SAB_REACH_EXPECT="REACH-RUN-WORDS-ONE"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    art->words++;'
SAB_AFTER='    art->words += 2;   /* SABOTAGE S573 */'
