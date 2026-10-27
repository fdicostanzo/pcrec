# S1683 ([INLINE-C] stage 2, design 9.1 S-IC28) -- `all` INCLUDES `code-c`.
# The enabled-set reader's `all` stops skipping the GRANT column's rows, so
# `--features all` (and a block's or a config's `features all`, and the
# library's "all") turns embedded code on. Witnesses: the refusals arm's
# `features all` rows, tests/code/t2/t2.rxt's second block, the library
# check.
SAB_ID="S1683-code-all-includes-codec"
SAB_FILE="src/parse/enabled.c"
SAB_SUITES="code"
SAB_DESC="the features set 'all' includes the invoker-only code-c module, so --features all grants embedded code"
SAB_REACH='"$PCREC" --features all -o "$REACH_TMP/o.c" --pattern '\''a(?C`c: return RX_PASS;`)b'\'' 2>&1; true'
SAB_REACH_EXPECT="which only the command-line option --allow-code=c"
SAB_COUNT=1
SAB_BEFORE='                if (!(rows[i].flags & RF_INVOKER_ONLY)) mask |= rows[i].feature;'
SAB_AFTER='                mask |= rows[i].feature;   /* SABOTAGE S1683 */'
