#!/usr/bin/env bash
# S903 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-13) -- under -fstartpos-guard=align the controller hands F the caller's RAW start position, not the aligned one, so a floor match at the aligned position is missed.
# `(?>\Ga|ab)c` is the VM witness (UNREACHED until B6); the DFA witness is `\Ga$|b$` under -fstartpos-guard=align, G2's align arm.
SAB_ID='S903-cmp13-align-raw-from'
SAB_FILE='src/gen/emit_compound.c'
SAB_SUITES='compound'
SAB_DESC='under -fstartpos-guard=align the controller hands F the caller'\''s RAW start position, not the aligned one, so a floor match at the aligned position is missed'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): @@FIG903@@. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_printf(c, "        int r = %s(subject, subject_length, search_from, capture_spans);\n", a);'
SAB_AFTER='    pcrec_sb_printf(c, "        int r = %s(subject, subject_length, raw_from, capture_spans);\n", a);   /* SABOTAGE S903 */'
SAB_FILE2='src/gen/emit_dfa.c'
SAB_COUNT2=1
SAB_BEFORE2='                 "size_t search_from, ptrdiff_t (*capture_spans)[2]%s)\n{\n",'
SAB_AFTER2='                 "size_t search_from, ptrdiff_t (*capture_spans)[2]%s)\n{\n    size_t raw_from = search_from; (void)raw_from;\n",   /* SABOTAGE S903 */'
