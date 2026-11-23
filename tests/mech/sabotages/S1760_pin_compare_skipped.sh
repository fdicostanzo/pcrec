# S1760 ([INLINE-C] stage 3, inline_c.md S-IC12) -- THE PIN COMPARE IS
# SKIPPED: a `sha256` pin is parsed and stored but never compared with the
# digest of the bytes the reader parsed, so a stale pin passes. Witness:
# tests/code/run_code_tests.sh arm 13 (the mismatched lib/include rows,
# whose digest comes from sha256sum, not from pcrec).
SAB_ID="S1760-pin-compare-skipped"
SAB_FILE="src/parse/rxt_source.c"
SAB_SUITES="code"
SAB_DESC="pcrec_rxt_reach_verify skips every edge, so an include/lib pin that does not match the file's SHA-256 is accepted"
# The fixtures are copied to a SHORT path ([PIN-MSG-DEPTH]): pcrec_error.msg is cut at
# 256 bytes and the phrase sits after the path, so a deep $TREE/$REACH_TMP hid it.
SAB_REACH='R="${PCREC_TMPDIR:-/var/tmp/pcrec-$(id -un)}"; mkdir -p "$R"; S=$(mktemp -d "$R/r.XXXXXX"); cp -r "$TREE/tests/code/frag" "$S/f"; printf '\''include "%s/f/pin2_ok.rxt" sha256 0000000000000000000000000000000000000000000000000000000000000000\n\npattern z\n'\'' "$S" > "$S/e.rxt"; "$PCREC" -o "$S" "$S/e.rxt"; rc=$?; rm -rf "$S"; exit $rc'
SAB_REACH_EXPECT='sha256 pin mismatch'
SAB_COUNT=1
SAB_BEFORE='        if (!e->pin || !e->digest || !strcasecmp(e->pin, e->digest)) continue;'
SAB_AFTER='        if (1) continue; /* SABOTAGE S1760 */'
