#!/usr/bin/env bash
# S3525 ([MEMFN] R-47 unit U4, lane bsu4g, 2026-11-22) -- plant (a) of docs/design/memfn/block_span.md §10.2's sabotage table (job 708's `nib_drop`): the vector span's level block builds its two nibble tables without the stretch set's HIGHEST member, so a window holding that byte reads as a miss. Caught by G2-V unit (memfn/tests/g2_vspan.py, run_g2_win.sh section V): its sweeps put every byte value at a stretch position and hold the answer to python re over the class the test writes. G2-V whole sees it too wherever a subject holds the dropped byte.
SAB_ID='S3525-vspan-nibble-table-drops-member'
SAB_FILE='memfn/src/window.c'
SAB_SUITES='g2v'
SAB_DESC='the vector span level block drops the highest member of the stretch set from its nibble tables'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3525. docs/dev/lanes/bsu4g_report.md carries the lane run.'
# REACH: the k 16 window witness (D-hors, B 16); its level block's last line, written by the
# same function right after the anchored table loop, as the clean tree writes it.
SAB_REACH='"$PCREC" --features all -fmemfn-simd=x86-64-v3 -p rx -o - --pattern "[0-9a-f]{17}"'
SAB_REACH_EXPECT='    return rx_mf1_vs0__w32_b(p + (16 - 16));'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (in_set(w->set[st->i], x)) {'
SAB_AFTER='        if (in_set(w->set[st->i], x) && ({ unsigned y_ = x + 1; while (y_ < 256 && !in_set(w->set[st->i], y_)) y_++; y_ < 256; })) {   /* SABOTAGE S3525 */'
