# S1763 ([INLINE-C] stage 3, inline_c.md S-IC31) -- THE FIRST CHAIN'S
# VERDICT IS USED: a file reached by a pinned chain and an unpinned one is
# judged by whichever chain the walk meets first, so declaration order
# decides trust. Witness: tests/code/run_code_tests.sh arm 13's dual chain
# in "ab" order (the pinned lib line first).
SAB_ID="S1763-first-chain-verdict"
SAB_FILE="src/parse/rxt_source.c"
SAB_SUITES="code"
SAB_DESC="pcrec_rxt_reach_unpinned answers from the first chain found rather than searching for any chain holding an unpinned line"
SAB_REACH='cd "$REACH_TMP" && printf '\''pattern c(?C`c: return RX_PASS;`)d\nname dc\n'\'' > c.rxt && hc=$(sha256sum c.rxt | cut -c1-64) && printf '\''lib "c.rxt" sha256 %s\n\npattern aa\nname da\n'\'' "$hc" > a.rxt && printf '\''lib "c.rxt" sha256 %s\n\npattern bb\nname db\n'\'' "$hc" > b.rxt && ha=$(sha256sum a.rxt | cut -c1-64) && printf '\''lib "a.rxt" sha256 %s\nlib "b.rxt"\ntarget t = u\n\npattern (?&dc)\nname u\nfeatures recursion,named-groups\n'\'' "$ha" > ab.rxt && "$PCREC" --allow-code=c -o "$REACH_TMP" ab.rxt'
SAB_REACH_EXPECT='ab.rxt:2 carries no sha256 pin'
SAB_COUNT=1
SAB_BEFORE='    const RxtReachEdge *hit = reach_search(g, real, true, NULL, 0, &depth, &oom);'
SAB_AFTER='    const RxtReachEdge *p1[64], *hit = NULL; reach_search(g, real, false, p1, 64, &depth, &oom); for (size_t k = 0; k < depth && k < 64 && !hit; k++) if (!p1[k]->pin) hit = p1[k]; /* SABOTAGE S1763 */'
