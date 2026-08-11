# S12 — disjoint_run_len always reports the whole list as one disjoint run,
# defeating rule 2's overlap guard for the M2.8 alternation trie
# (tests/codegen/CLAUDE.md run_trie_identity.sh table, row 1). This is the
# MEMORY-SAFE form of the disjointness sabotage; do NOT use the "naive rule-1"
# form documented alongside it (see NOT-ENCODABLE notes in the final report —
# that one is a 32-byte arena over-read with an unstable count).
# Documented result: 2 .rxt cases / 21 @200 / 64 @500.
SAB_ID="S12-disjoint-run-len-off"
SAB_FILE="src/ir/nfa.c"
SAB_SUITES="trie"
SAB_DESC="disjoint_run_len: 'return n;' as the first statement (disjointness guard off)"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 2 .rxt / 21 @200 / 64 @500"
SAB_COUNT=1
SAB_BEFORE="static int disjoint_run_len(const TItem *items, int n, int depth)
{
    /* 257 is a HARD bound, not a heuristic: every bitmap in \`known\` is"
SAB_AFTER="static int disjoint_run_len(const TItem *items, int n, int depth)
{
    return n;
    /* 257 is a HARD bound, not a heuristic: every bitmap in \`known\` is"
