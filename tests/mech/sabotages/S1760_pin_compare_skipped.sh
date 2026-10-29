# S1760 ([INLINE-C] stage 3, inline_c.md S-IC12) -- THE PIN COMPARE IS
# SKIPPED: a `sha256` pin is parsed and stored but never compared with the
# digest of the bytes the reader parsed, so a stale pin passes. Witness:
# tests/code/run_code_tests.sh arm 13 (the mismatched lib/include rows,
# whose digest comes from sha256sum, not from pcrec).
SAB_ID="S1760-pin-compare-skipped"
SAB_FILE="src/parse/rxt_source.c"
SAB_SUITES="code"
SAB_DESC="pcrec_rxt_reach_verify skips every edge, so an include/lib pin that does not match the file's SHA-256 is accepted"
SAB_REACH='printf '\''include "%s/tests/code/frag/pin_ok.rxt" sha256 0000000000000000000000000000000000000000000000000000000000000000\n\npattern z\n'\'' "$TREE" > "$REACH_TMP/e.rxt"; "$PCREC" -o "$REACH_TMP" "$REACH_TMP/e.rxt"'
SAB_REACH_EXPECT='sha256 pin mismatch'
SAB_COUNT=1
SAB_BEFORE='        if (!e->pin || !e->digest || !strcasecmp(e->pin, e->digest)) continue;'
SAB_AFTER='        if (1) continue; /* SABOTAGE S1760 */'
