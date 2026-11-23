# S1761 ([INLINE-C] stage 3, inline_c.md S-IC13) -- ONLY THE LAST LINK OF A
# CHAIN IS CHECKED: the chain walk forgets an unpinned line it already
# crossed, so entry -> (unpinned) middle -> (pinned) leaf trusts the leaf's
# code. Witness: tests/code/run_code_tests.sh arm 13's three-file chain
# (frag/pin1_entry.rxt -> pin2_ok.rxt -(no pin)-> pin3_mid.rxt -> pin4_leaf.rxt).
SAB_ID="S1761-pin-last-link-only"
SAB_FILE="src/parse/rxt_source.c"
SAB_SUITES="code"
SAB_DESC="the reach walk judges each edge alone instead of carrying the chain's first unpinned line, so a pinned last link hides an unpinned middle"
# Fixtures copied to a SHORT path ([PIN-MSG-DEPTH]; see S1760): the 256-byte message cut.
SAB_REACH='R="${PCREC_TMPDIR:-/var/tmp/pcrec-$(id -un)}"; mkdir -p "$R"; S=$(mktemp -d "$R/r.XXXXXX"); cp -r "$TREE/tests/code/frag" "$S/f"; "$PCREC" --allow-code=c -o "$S/o.c" --include-block "$S/f/pin4_leaf.rxt:6" "$S/f/pin1_entry.rxt"; rc=$?; rm -rf "$S"; exit $rc'
SAB_REACH_EXPECT='pin2_ok.rxt:5 carries no sha256 pin'
SAB_COUNT=1
SAB_BEFORE='        const RxtReachEdge *f = first ? first : e->pin ? NULL : e;'
SAB_AFTER='        const RxtReachEdge *f = e->pin ? NULL : e; (void)first; /* SABOTAGE S1761 */'
