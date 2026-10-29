# S1762 ([INLINE-C] stage 3, inline_c.md S-IC14) -- THE LOCAL EXEMPTION
# REACHES AN INCLUDED FILE: a block compiled through `--include-block` is
# judged as if it were the entry's own, so its code compiles with no pin.
# Witness: tests/code/run_code_tests.sh arm 13 (an unpinned include line:
# the fragment's code is refused).
SAB_ID="S1762-local-reaches-include"
SAB_FILE="src/parse/mod_code.c"
SAB_SUITES="code"
SAB_DESC="the code port ignores the emit input's code_origin, so an included fragment's block is LOCAL and needs no pin"
SAB_REACH='"$PCREC" --allow-code=c -o "$REACH_TMP/o.c" --include-block "$TREE/tests/code/frag/pin4_leaf.rxt:6" "$TREE/tests/code/frag/pin1_entry.rxt"'
SAB_REACH_EXPECT='embedded code at'
SAB_COUNT=1
SAB_BEFORE='    const char *real = def ? def->file_real : in ? in->code_origin : NULL;'
SAB_AFTER='    const char *real = def ? def->file_real : NULL; /* SABOTAGE S1762 */'
