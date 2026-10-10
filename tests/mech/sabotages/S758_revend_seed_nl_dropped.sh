#!/usr/bin/env bash
# S758 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- the walk's n-1 seed dropped: a `$`/`\Z` match ending before a final newline is lost.
# Detector: the answer net: `\d+$` on "abc123\n" and `a*$` on "aa\n" answer NOMATCH or the empty end match.
SAB_ID='S758-revend-seed-nl-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_DESC='the walk'\''s n-1 seed dropped: a `$`/`\Z` match ending before a final newline is lost'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S758.'
SAB_HARNESS_TARGET='tests/assertions/rev_end.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\s+$" && grep -q "for (int revend_seed = 0;" "$REACH_TMP/o.c" && echo REACH-WALK'
SAB_REACH_EXPECT='REACH-WALK'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='               tie ? "    int revend_tie = 0;\n" : "", eol ? 2 : 1);'
SAB_AFTER='               tie ? "    int revend_tie = 0;\n" : "", eol ? 1 : 1);   /* SABOTAGE S758 */'
