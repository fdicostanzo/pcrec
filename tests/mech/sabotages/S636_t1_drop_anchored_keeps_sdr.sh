#!/usr/bin/env bash
# S636 ([DEC-FALLBACK] B2, lane decfbB2) -- drop-anchored's sets cell keeps size_drop_rung, so the anchored machine would be built again and the retry refuse (K53 restored).
# S-F15. Detector at B2: the oracle's post-row sdr check on \p{L} -e utf8 (fbt (a) seq-anch, (d) or-anch); from B3 run_anchored_match.sh's K53 cell.
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S636-t1-drop-anchored-keeps-sdr'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="drop-anchored's sets cell keeps size_drop_rung, so the anchored machine would be built again and the retry refuse (K53 restored)"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S636. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .sets = { FIT_DD_KEEP, FIT_CR_KEEP, FIT_SDR_TO_ANCHORED, 0, 0, false, false },'
SAB_AFTER='      .sets = { FIT_DD_KEEP, FIT_CR_KEEP, FIT_SDR_KEEP, 0, 0, false, false },   /* SABOTAGE S636 */'
