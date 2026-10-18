#!/usr/bin/env bash
# S1115 ([ENTRY-TABLE] E1, lane e1; compound_entries.md §3.0 I5, §3.6
# "length neutrality") -- THE SIZE DECISIONS READ THE MARKS. The caps, the
# size term and every figure a refusal or note quotes read the text through
# `pcrec_sb_size_decide`, which subtracts the part-layout marks' bytes, so no
# control can move a decision. Planted, a controlled compile's decision sizes
# exceed the default's by the marks. Seen by the neutral arm (the
# `--warn-emit-bytes` note's figures must be the no-control compile's).
SAB_ID="S1115-partlayout-marks-counted"
SAB_FILE="src/core/sb.c"
SAB_SUITES="partlayout"
SAB_DESC='pcrec_sb_size_decide stops subtracting the part-layout marks, so a control moves the size figures every cap, the size term and the size notes read'
SAB_DOC_FIGURE="MEASURED by lane e1 2026-10-18 (one mech row, solo, Linux dev box, at b57d43101^): partlayout:1fail/45pass, DETECTED, against a clean 0fail/46pass. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1115."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx --part-layout=prefilter:inline -o "$REACH_TMP/x.c" --pattern "(a)b" && grep -h "RX_PART_LAYOUT" "$REACH_TMP/x.c"'
SAB_REACH_EXPECT='#define RX_PART_LAYOUT "prefilter=inline"'
SAB_BEFORE='    z.total  -= sb->layout_bytes;    /* [ENTRY-TABLE] E1: the marks'"'"' code bytes */'
SAB_AFTER='    /* SABOTAGE S1115: the marks'"'"' bytes reach the decision */'
