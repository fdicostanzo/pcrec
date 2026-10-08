#!/usr/bin/env bash
# S634 ([DEC-FALLBACK] B2, lane decfbB2) -- drop-premul's sets cell stops OR-ing PCREC_NO_PREMUL_TABLE, so the retry would rebuild the same premultiplied artifact and refuse again.
# S-F12. Detector at B2: the oracle's post-row flags check on lowboth (*UCP)(?i)[\dk] -e utf8 (fbt (a) seq-premul, (d) or-premul); from B3 the retry refuses.
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S634-t1-drop-premul-no-flag'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="drop-premul's sets cell stops OR-ing PCREC_NO_PREMUL_TABLE, so the retry would rebuild the same premultiplied artifact and refuse again"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S634. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .sets = { FIT_DD_KEEP, FIT_CR_KEEP, FIT_SDR_TO_PREMUL, PCREC_NO_PREMUL_TABLE, 0,'
SAB_AFTER='      .sets = { FIT_DD_KEEP, FIT_CR_KEEP, FIT_SDR_TO_PREMUL, 0, 0,   /* SABOTAGE S634 */'
