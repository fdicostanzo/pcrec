# S327 — [FINDINGS] B5 A `cpfreq` KEY MAY NAME A SURROGATE
# (src/parse/rxt_source.c, `row_key`): the scalar-value test is gone, so
# `row U+D800 3` parses, and `encode-utf8` would derive the ill-formed
# ED A0 80 — bytes no valid UTF-8 subject holds — onto a utf8 compile's rate.
SAB_ID="S327-findings-cp-key-surrogate"
SAB_FILE="src/parse/rxt_source.c"
SAB_SUITES="rxtsource"
SAB_DESC="row_key accepts a surrogate code point (U+D800..U+DFFF) as a cpfreq key — decoded text never holds one, and encode-utf8 would derive ill-formed bytes from it"
SAB_DOC_FIGURE="rxtsource: findings/B0/cp-key-surr ACCEPTED (red); the B5 control (surrogate EDGES U+D7FF/U+E000 accept) stays green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S327."
# [MECH-REACH] a cpfreq key is read by this function: the shipped weblog's
# cpfreq rows list back through --list-analysis.
SAB_REACH='"$PCREC" --list-analysis weblog | grep -c "^U+"'
SAB_REACH_EXPECT="86"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (k >= 0xD800 && k <= 0xDFFF)'
SAB_AFTER='    if (k >= 0xD800 && k <= 0xDFFF && 0)   /* SABOTAGE S327 */'
