# S14 — the trie only fires for alternations with >= 100 branches
# (tests/codegen/CLAUDE.md run_trie_identity.sh table, row 4; this is the
# ORIGINAL R3.3-era sabotage that defeated the first version of the identity
# check, which had only a 256-branch control). Documented result: 0 differ on
# the sweep — only the 4- and 8-branch controls fire (the 256-branch control
# still exceeds the new threshold and passes).
SAB_ID="S14-nbr-100-threshold"
SAB_FILE="src/ir/nfa.c"
SAB_SUITES="trie"
SAB_DESC="A_ALT eligibility: add '&& nbr >= 100' so the trie only fires above 100 branches"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 0 differ — only the 4- and 8-branch controls fire"
SAB_COUNT=1
SAB_BEFORE="            elig[j] = TRIE_ENABLED && trie_key(b, br[j], &keys[j]);"
SAB_AFTER="            elig[j] = TRIE_ENABLED && nbr >= 100 && trie_key(b, br[j], &keys[j]);"
