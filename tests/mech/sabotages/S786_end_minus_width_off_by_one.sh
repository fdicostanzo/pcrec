#!/usr/bin/env bash
# S786 ([START-LANDING] SL2, lane slbuild; docs/design/start_landing.md §7.5 rows 6-7; docs/dev/lanes/slbuild_report.md) -- the end-minus-width start off by one (row 6, the width in characters, has no separate plant: its witness `é` is [facts-sl1]'s [2,2] literal and this row's detector).
# Detector: run_start_landing.sh §5 (answers against the triple-deny build); the corpus harness on every fixed-width pattern.
SAB_ID='S786-end-minus-width-off-by-one'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='startlanding harness'
SAB_DESC='the end-minus-width start subtracts W - 1, so every fixed-width match is reported one byte short at its start'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S786.'
# RE-AIMED 2026-10-23 (lane s3fix600, D172 S3 job 600): the witness is a fixed-width
# window, a `cover` artifact by default (no scan, so not this site); the probe's
# compile takes the cover row's deny --memfn=no-window-search, the build before S3.
SAB_REACH='"$PCREC" --memfn=no-window-search -p rx -o "$REACH_TMP/o.c" --pattern "abcd" && grep -q "last_accept_position - 4;" "$REACH_TMP/o.c" && echo REACH-EMW'
SAB_REACH_EXPECT='REACH-EMW'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, "    size_t match_start_position = last_accept_position - %lld;\n", w);'
SAB_AFTER='        pcrec_sb_printf(c, "    size_t match_start_position = last_accept_position - %lld;\n", w - 1);   /* SABOTAGE S786 */'
