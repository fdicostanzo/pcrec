# S1721 ([INLINE-C] stage 2, review 2026-10-27-r1-ic2 F22) -- A SEGMENT
# FALLING OFF ITS END SEGFAULTS instead of trapping: the generated function
# ends in a null store rather than `__builtin_trap()`. The program still
# dies by a signal, which the old any-signal trap test accepted. Witness:
# tests/code/run_code_tests.sh arm 8, "a segment falling off its end", which
# now wants __builtin_trap's own signal.
SAB_ID="S1721-code-falloff-segfaults"
SAB_FILE="src/gen/emit_code.c"
SAB_SUITES="code"
SAB_DESC="a code segment that falls off its end dies by SIGSEGV (a null store) instead of __builtin_trap's signal"
SAB_REACH='"$PCREC" --allow-code=c -o "$REACH_TMP/o.c" --pattern '\''a(?C`c: return RX_PASS;`)b'\'' && grep -c "__builtin_trap(); }" "$REACH_TMP/o.c"'
SAB_REACH_EXPECT='1'
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_puts(c, "\n__builtin_trap(); }\n");'
SAB_AFTER='    pcrec_sb_puts(c, "\n*(volatile int *)0 = 0; }\n");   /* SABOTAGE S1721 */'
