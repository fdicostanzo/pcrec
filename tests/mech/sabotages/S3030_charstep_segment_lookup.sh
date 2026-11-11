#!/usr/bin/env bash
# S3030 ([UCP] U3, review 2026-11-10 r4 ucpu3 checks-4/9, lane ucpu3fix) -- THE
# CHARACTER-STEPPED DFA'S SEGMENT LOOKUP IS OFF BY ONE AT EVERY SEGMENT'S FIRST
# CODE POINT. `<prefix>_isl_seg`'s binary search takes `lo[m] < cp` for
# `<=`, so the first code point of each segment reads as the segment before
# it. Measured at landing: the subject tip's corpus caught it on one pattern
# (13 cells, the `é\b` literal); the EDGE blocks of tests/ucp/island.rxt
# catch it on every set (3,936 of 8,728 cells).
SAB_ID="S3030-charstep-segment-lookup"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="charstep"
SAB_DESC="the character-stepped DFA's segment lookup reads a segment's first code point as the segment before it"
SAB_DOC_FIGURE='charstep arm: 3936 of 8728 corpus cells red (measured at landing, lane ucpu3fix); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3030.'
SAB_REACH='"$PCREC" -e utf8 --features all -p rx -o "$REACH_TMP/o0.c" --pattern "(*UCP)\\b\\w+\\b" >/dev/null 2>&1 && grep -c "define RX_DFA_SCAN \"char-step\"" "$REACH_TMP/o0.c"'
SAB_REACH_EXPECT="1"
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='        "        if (lo[m] <= cp) a = m; else b = m - 1;\n"'
SAB_AFTER='        "        if (lo[m] < cp) a = m; else b = m - 1;\n"   /* SABOTAGE S3030 */'
