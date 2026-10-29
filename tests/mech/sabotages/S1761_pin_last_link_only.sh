# S1761 ([INLINE-C] stage 3, inline_c.md S-IC13) -- ONLY THE LAST LINK OF A
# CHAIN IS CHECKED: the chain walk forgets an unpinned line it already
# crossed, so entry -> (unpinned) middle -> (pinned) leaf trusts the leaf's
# code. Witness: tests/code/run_code_tests.sh arm 13's three-file chain
# (frag/pin_entry.rxt -> pin_mid.rxt -> pin_leaf.rxt).
SAB_ID="S1761-pin-last-link-only"
SAB_FILE="src/parse/rxt_source.c"
SAB_SUITES="code"
SAB_DESC="the reach walk judges each edge alone instead of carrying the chain's first unpinned line, so a pinned last link hides an unpinned middle"
SAB_REACH='"$PCREC" --allow-code=c -o "$REACH_TMP/o.c" --include-block "$TREE/tests/code/frag/pin_leaf.rxt:6" "$TREE/tests/code/frag/pin_entry.rxt"'
SAB_REACH_EXPECT='pin_entry.rxt:8 carries no sha256 pin'
SAB_COUNT=1
SAB_BEFORE='        const RxtReachEdge *f = first ? first : e->pin ? NULL : e;'
SAB_AFTER='        const RxtReachEdge *f = e->pin ? NULL : e; (void)first; /* SABOTAGE S1761 */'
