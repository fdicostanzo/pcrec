# S13 — the shipped (non -DPCREC_NO_TRIE) build also gets TRIE_ENABLED = 0,
# so the whole M2.8 factoring path is off unconditionally
# (tests/codegen/CLAUDE.md run_trie_identity.sh table, row 3). Documented
# result: 0 differ on the random sweep (both builds are now unfactored and
# trivially agree) — ONLY the positive controls fire, because the 4/8/256
# branch patterns were specifically built to exceed the DFA state cap unless
# factored. This is the case the tool exists to make loud: a sabotage that is
# INVISIBLE to the main equivalence sweep and caught only by the controls.
SAB_ID="S13-trie-off-shipped"
SAB_FILE="src/ir/nfa.c"
SAB_SUITES="trie"
SAB_DESC="enum { TRIE_ENABLED = 1 } -> = 0 in the #else (shipped, non -DPCREC_NO_TRIE) branch"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 0 differ on the sweep — only the controls fire"
SAB_COUNT=1
SAB_BEFORE="enum { TRIE_ENABLED = 1 };"
SAB_AFTER="enum { TRIE_ENABLED = 0 };"
