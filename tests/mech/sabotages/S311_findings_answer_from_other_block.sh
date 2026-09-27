# S311 — [FINDINGS] B2 F-5 (adapted to B2's one kind): A QUERY'S ANSWER IS
# DERIVED FROM A BLOCK OTHER THAN THE ONE THE SELECTION RULE PICKED
# (src/core/findings.c, `find_derive_byte_rate`): the serves line of one
# link's block matches, and the counts normalized are the chain TERMINAL's —
# design §0.3's "every query is answered from EXACTLY ONE block" broken,
# the per-query blending R9 forbids. (The design's F-5 names run-rarity's
# P(first); `bigram` is B4's, so the row plants the same defect on the one
# query B2 has.)
#
# Detector: every run_findings_tests.sh §6 fixture whose answer is a user
# bundle's own block — its stamp carries the terminal default's digest
# instead of findings_ref.py's for that bundle.
SAB_ID="S311-findings-answer-from-other-block"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC="the byte-rate is normalized from the chain terminal's block whenever a user bundle's block is the one whose serves line matched — two blocks feeding one query, the blending design §0.3/R9 forbids"
SAB_DOC_FIGURE="findings red on the §6 fixtures answered by a user bundle (#1, #2, #5, #7, #11 utf8, #12, #14, #17, #20, #21): each stamps the default's digest. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S311."
SAB_REACH='"$PCREC" -p rx -I "$TREE/tests/findings/adversarial" --analysis onehot-e -o "$REACH_TMP/a.c" --pattern "abc" && grep -q "^#define RX_FINDINGS \"byte-rate=onehot-e:" "$REACH_TMP/a.c" && echo REACH-FINDINGS-USER-BLOCK-ANSWERS'
SAB_REACH_EXPECT="REACH-FINDINGS-USER-BLOCK-ANSWERS"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    nr = pcrec_find_normalize(fb->counts, fr->byte_rate);'
SAB_AFTER='    /* SABOTAGE S311: the answer read from the terminal block */
    nr = pcrec_find_normalize(chain->links[chain->n - 1].nblocks
                              ? chain->links[chain->n - 1].blocks[0].counts
                              : fb->counts, fr->byte_rate);'
