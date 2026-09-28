# S308 — [FINDINGS] B2 F-2: THE SELECTION RULE IGNORES THE `when` LIST
# (src/core/findings.c, `pcrec_find_chain_answer`): a block answers a query
# under EVERY encoding, whatever its `serves ... when` line declares — so the
# shipped default, which declares `byte` only because its flat 0x80-0xff half
# would call a UTF-8 lead byte the rarest byte there is, leaks into `-e utf8`
# (design §2.4 "use what the data declares"; §11.2 F-2).
#
# ANSWER-NEUTRAL BY CONSTRUCTION (a rate moves speed, never an answer), so the
# detector is the STAMP and the resolution: run_findings_tests.sh §4's two
# `-e utf8` cells expect `byte-rate=none` and read the default's digest, and
# §6 #11/#3/#1's utf8-only and byte-only fixtures answer from the wrong link.
SAB_ID="S308-findings-when-ignored"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC="pcrec_find_chain_answer takes the first block with a serves line for the query WHATEVER its when list says, so the shipped default (declared byte only) answers -e utf8 compiles and every per-encoding fall-through resolves to the wrong link — the gate D122-2(3) put in the data, ignored"
SAB_DOC_FIGURE="findings red on §4 [utf8, DFA]/[utf8, VM] (the default's digest where byte-rate=none is expected) and on the §6 per-encoding fixtures (#3, #11, the no-query note). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S308."
# [MECH-REACH] the site answers: under -e utf8 the default declares nothing,
# and a bundle declaring utf8 answers it.
SAB_REACH='"$PCREC" -p rx -e utf8 -o "$REACH_TMP/a.c" --pattern "abc" && grep -q "^#define RX_FINDINGS \"byte-rate=none\"" "$REACH_TMP/a.c" && "$PCREC" -p rx -e utf8 -I "$TREE/tests/findings/adversarial" --analysis uniform -o "$REACH_TMP/b.c" --pattern "abc" && grep -q "^#define RX_FINDINGS \"byte-rate=uniform:" "$REACH_TMP/b.c" && echo REACH-FINDINGS-WHEN-LIST'
SAB_REACH_EXPECT="REACH-FINDINGS-WHEN-LIST"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                    encs_list(fb->serves[j].encs, enc)) {'
SAB_AFTER='                    (encs_list(fb->serves[j].encs, enc) || 1)) {   /* SABOTAGE S308: the when list ignored */'
