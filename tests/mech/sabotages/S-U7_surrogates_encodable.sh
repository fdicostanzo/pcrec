# S-U7 ([M5.0] stage 2; utf8_design.md §8.2, §8.3.1) -- THE SURROGATE RANGE
# IS ENCODABLE.
#
# THE CLAIM: U+D800-U+DFFF are ABSENT from every lowered set (§2.3's split),
# which is half of where §2.6's "ill-formed matches nothing" ruling comes
# from: a compiled `.` REJECTS the three-byte surrogate spelling `ED A0 80`
# because no automaton path exists, not because anything validates.
#
# THE SABOTAGE merges the surrogate gap back into the 3-byte band, so the
# decomposition happily emits `ED A0-BF 80-BF` transitions and the artifact
# ACCEPTS CESU-8-shaped input.
#
# THE WITNESS IS A SUBJECT, NOT A PATTERN (r54 C5, §8.3.1): nothing about
# what COMPILES changes — the parser still refuses a written `\x{d800}` —
# so a compile-time refusal corpus scores this row green while the automaton
# quietly grows six thousand ill-formed strings. Only a subject-level cell
# (`^.$` vs `ED A0 80`) distinguishes the two builds.
SAB_ID="S-U7-surrogates-encodable"
SAB_FILE="src/opt/lower_enc.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8"
SAB_DESC="the utf8 decomposition's band table loses its surrogate gap, so a lowered '.', '[^a]' or wide range accepts the UTF-8-shaped encodings of U+D800..U+DFFF that valid UTF-8 does not contain"
SAB_DOC_FIGURE="PREDICTED (§8.3.1): the 9 surrogate-subject blocks of tests/utf8/invalid.rxt red (the artifact ACCEPTS ED A0 80 / ED BF BF where the expectation is reject); every compile-time cell green, which is the row's own point. DEMONSTRATED at stage 2 pre-corpus: -e utf8 '^.$' rejects ED A0 80 clean and matches (0,3) sabotaged."
SAB_REACH='"$PCREC" -e utf8 -p rx -o - -- "^.$"'
SAB_REACH_EXPECT='Pattern: ^.$'
SAB_REACH_POP='tests/utf8/invalid.rxt|ED A0|9'
SAB_COUNT=1
SAB_BEFORE='        { 0x800,   0xD7FF,   3 },
        /* U+D800–U+DFFF: no encoding — deliberately no band. */
        { 0xE000,  0xFFFF,   3 },'
SAB_AFTER='        { 0x800,   0xFFFF,   3 },  /* SABOTAGE S-U7: surrogates encodable */'
