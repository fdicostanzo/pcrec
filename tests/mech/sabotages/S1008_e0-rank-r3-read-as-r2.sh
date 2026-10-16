#!/usr/bin/env bash
# S1008 ([COMPOUND] E0, lane e0build; docs/design/compound_entries.md §3.6) -- the rank column's R3 cell reads as R2: the hybrid's embedded search ranks per call even where the attempt loop's retry re-seeds from it.
SAB_ID='S1008-e0-rank-r3-read-as-r2'
SAB_FILE='src/gen/entries.c'
SAB_SUITES='compound'
SAB_DESC='entry_rows[] ranks search_run -> prefilter R2 where the retry re-enters the embedded search (an MRL clamp or an adaptive re-seed), which the layout row (E1) would read as not hot'
SAB_DOC_FIGURE='HAND-MEASURED by lane e0build 2026-10-16 (plant applied to the lane tree, libpcrec.a and the drive rebuilt, check_entry_ranks.py --every 8): 115 FAIL lines (the two R3 fixture rows; 114 re-seed population artifacts whose search_run holds two prefilter call sites; the R3 floor, 0 of 56). The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# REACH: a clamped hybrid's search_run still calls the embedded search twice
# (the entry and the retry's re-seed), the site an R3 rank describes.
SAB_REACH='"$PCREC" -p rx --features all -o - --pattern "(a+)bcd" | grep -c "rx_prefilter(subject"'
SAB_REACH_EXPECT='2'
SAB_BEFORE='    return s->prefilter_retry ? PCREC_RANK_R3_INNER : PCREC_RANK_R2_PER_CALL;'
SAB_AFTER='    return PCREC_RANK_R2_PER_CALL;   /* SABOTAGE S1008 */'
