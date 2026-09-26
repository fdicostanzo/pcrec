# S291 — [FINDINGS] B0 (r2 M-B3): an `analysis` bundle inside an `include`
# fragment is refused in the FRAGMENT's own sub-parse, but the refusal no
# longer reaches the ENTRY's parse.
#
# `src/parse/rxt_source.c`'s `fragment_check` drops the propagation arm:
# every fragment outcome, the fragment rule's refusal included, is treated
# as leg B's [resolution] class. The entry then parses clean with a bundle
# in its closure that no resolution stop will ever read — dead text, the
# thing D123-8 item 3's corollary ruled a parse error.
#
# DETECTOR: tests/rxtsource's `[FINDINGS] B0` section, the
# `analysis_in_fragment.rxtin` cell (bundle two include links down).
SAB_ID="S291-fragment-bundle-not-propagated"
SAB_FILE="src/parse/rxt_source.c"
SAB_SUITES="rxtsource"
SAB_DESC="a fragment's analysis-bundle refusal is swallowed like any other fragment failure, so an entry whose include closure carries a bundle parses clean"
SAB_DOC_FIGURE="docs/design/findings/design.md §9 (analysis block in an include fragment); docs/spec/rxt_format.md's analysis section"
SAB_COUNT=1
# REACH: on the clean tree the fixture's entry parse must fail WITH the
# fragment rule's own sentence, naming the leaf — which is the propagation
# arm this plant removes, reached.
SAB_REACH='"$PCREC" --list-source "$TREE/tests/rxtsource/fixtures/analysis_in_fragment.rxtin"'
SAB_REACH_EXPECT='analysis_frag_leaf.rxtfrag:3: '"'"'analysis leaked'"'"' is in an include fragment'
SAB_BEFORE='    if (!refused) return 0;'
SAB_AFTER='    return 0;   /* SABOTAGE S291: the fragment rule is swallowed */'
