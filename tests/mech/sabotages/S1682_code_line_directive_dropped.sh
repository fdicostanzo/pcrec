# S1682 ([INLINE-C] stage 2, design 9.1 S-IC10) -- `#line` IS DROPPED. A
# segment's function is emitted without the `#line` that maps its text to
# the pattern file, so gcc reports an error in the user's code at a line of
# the generated .c (goal 4, DT-3.3). Witness: tests/code/run_code_tests.sh
# arm 5, "a segment's error names its .rxt line and column".
SAB_ID="S1682-code-line-directive-dropped"
SAB_FILE="src/gen/emit_code.c"
SAB_SUITES="code"
SAB_DESC="a code segment written as one source line is emitted without its #line, so a compile error in it names the generated file"
SAB_REACH='"$PCREC" --allow-code=c -o "$REACH_TMP/o.c" --pattern '\''a(?C`c: return RX_PASS;`)b'\'' && grep -F "#line 1 \"<command line>\"" "$REACH_TMP/o.c"'
SAB_REACH_EXPECT='#line 1 "<command line>"'
SAB_COUNT=1
SAB_BEFORE='    if (!esc) {
        code_line_dir(c, line, file);'
SAB_AFTER='    if (!esc) {   /* SABOTAGE S1682: no #line */'
