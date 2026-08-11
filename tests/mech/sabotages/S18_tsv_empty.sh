# S18 — pcrec_syntax_tsv() (backs --list-syntax) returns an empty string
# instead of the registry dump (tests/reject/CLAUDE.md's SR-4 table, row 3).
# Documented result: 0 hand-written fail, 0 iterated fail, but the harness's
# OWN vacuity guard fires (an iteration loop over zero rows must not silently
# report "0 failures" as success). This sabotage's job is to prove that guard
# exists and works, not to move the fail count.
SAB_ID="S18-tsv-empty"
SAB_FILE="src/parse/syntax_dump.c"
SAB_SUITES="reject"
SAB_DESC="pcrec_syntax_tsv(): early 'return strdup(\"\");' before any row is rendered"
SAB_DOC_FIGURE="tests/reject/CLAUDE.md: 0/0, but the vacuity guard fires"
SAB_COUNT=1
SAB_BEFORE="char *pcrec_syntax_tsv(unsigned flavours)
{
    StrBuf sb = {0};"
SAB_AFTER="char *pcrec_syntax_tsv(unsigned flavours)
{
    StrBuf sb = {0};
    return strdup(\"\");"
