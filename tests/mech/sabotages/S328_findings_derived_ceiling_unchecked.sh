# S328 — [FINDINGS] B5 THE DERIVED-COUNT CEILING IS NOT CHECKED AT PARSE
# (src/parse/rxt_source.c, `fblock_close_check`): a `cpfreq` block whose
# rows each obey PCREC_MAX_FIND_COUNT but whose encode-utf8 derivation puts
# more than it on one shared lead byte parses, and the compile that reads it
# normalizes a count the §2.5 arithmetic bound does not cover (the accessor
# would then report it as an INTERNAL error, not by the limit's name).
SAB_ID="S328-findings-derived-ceiling-unchecked"
SAB_FILE="src/parse/rxt_source.c"
SAB_SUITES="rxtsource"
SAB_DESC="fblock_close_check never refuses: a cpfreq block whose derived byte count exceeds PCREC_MAX_FIND_COUNT (two code points sharing a lead byte) parses instead of being refused by the limit's name"
SAB_DOC_FIGURE="rxtsource: findings/B0/cp-derived-over ACCEPTED (red); the B5 control (2^40 on an unshared byte accepts) stays green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S328."
# [MECH-REACH] the close check runs on a real cpfreq block: the shipped
# weblog parses (and so passed through it) and lists a cpfreq section.
SAB_REACH='"$PCREC" --list-analysis weblog | grep -c "^#section cpfreq"'
SAB_REACH_EXPECT="1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for (size_t j = 0; fb->cps && j < fb->nserves; j++)'
SAB_AFTER='    for (size_t j = 0; fb->cps && j < fb->nserves && 0; j++)   /* SABOTAGE S328 */'
