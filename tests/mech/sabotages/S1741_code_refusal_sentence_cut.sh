# S1741 ([INLINE-C] stage 2, lane ic2d27land, D27 finding F2) -- THE CODE
# REFUSAL SENTENCE IS LONGER THAN pcrec_error.msg again: the lone-carriage-
# return refusal (the longest `what`) is cut at 255 bytes mid-word, as
# "...what the compiler compi". Witness: tests/code/d27 ref_cr_lone, whose
# stderr must end with the sentence's last word and the offset.
SAB_ID="S1741-code-refusal-sentence-cut"
SAB_FILE="src/parse/mod_code.c"
SAB_SUITES="code"
SAB_DESC="the code-refusal sentence regains its long tail, so the carriage-return refusal is truncated mid-word by the 256-byte message cap"
SAB_REACH='"$PCREC" --allow-code=c -o "$REACH_TMP/o.c" --pattern-esc --pattern '\''"a(?C`c: /* x\ry */ return RX_PASS;`)b"'\'' 2>&1 | grep -c "carriage return"'
SAB_REACH_EXPECT='1'
SAB_COUNT=1
SAB_BEFORE='"byte %zu of the segment; the code a reviewer reads would "
               "differ from what gcc compiles", at,'
SAB_AFTER='"byte %zu of the segment; such characters make the code a "
               "reviewer reads differ from what the compiler compiles", at,   /* SABOTAGE S1741 */'
