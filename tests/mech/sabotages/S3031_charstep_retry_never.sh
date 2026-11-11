#!/usr/bin/env bash
# S3031 ([UCP] U3, review 2026-11-10 r4 ucpu3 checks-5/9, lane ucpu3fix) -- THE
# CHARACTER-STEPPED RETRY MACHINE NEVER SUCCEEDS. `<prefix>__retry` over an
# island notempty machine returns -1 always, so the find-all iterator loses
# the non-empty match after an empty one. The subject tip's corpus passed it
# (its `mc` counts take no retry); the `mg` cells of
# `(*UCP)\b(?:|\w+)` and `(*UCP)\b\w*?` catch it (33 cells at landing).
SAB_ID="S3031-charstep-retry-never"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="charstep"
SAB_DESC="the character-stepped retry machine always answers no match, so a find-all loses the non-empty match after an empty one"
SAB_DOC_FIGURE='charstep arm: 33 mg cells red (measured at landing, lane ucpu3fix); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3031.'
SAB_REACH='"$PCREC" -e utf8 --features all -p rx -o "$REACH_TMP/o0.c" --pattern "(*UCP)\\b(?:|\\w+)" >/dev/null 2>&1 && grep -c "_retry(const unsigned char" "$REACH_TMP/o0.c"'
SAB_REACH_EXPECT="1"
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    pcrec_sb_puts(c, "    if (last == (size_t)-1) return -1;\n"'
SAB_AFTER='    pcrec_sb_puts(c, "    if (last == (size_t)-1 || 1) return -1;\n"   /* SABOTAGE S3031 */'
