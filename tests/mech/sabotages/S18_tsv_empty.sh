# S18 — pcrec_syntax_tsv() (backs --list-syntax) returns an empty string
# instead of the registry dump (tests/reject/CLAUDE.md's SR-4 table, row 3).
# Documented result: 0 hand-written fail, 0 iterated fail, but the harness's
# OWN vacuity guard fires (an iteration loop over zero rows must not silently
# report "0 failures" as success). This sabotage's job is to prove that guard
# exists and works, not to move the fail count.
#
# RETAGGED 2026-08-12 (MOD-0.8c slice 1) with `registry` and `cli` — the two
# suites that CONSUME the dump this sabotage empties, both named in the docs
# as doing so. `registry` runs compliance_section.py, whose --check holds
# docs/pcre2_compliance.md's generated index to `pcrec --list-syntax`
# (tests/registry/CLAUDE.md), and `cli` runs case10, which src/parse/CLAUDE.md
# cites as the assertion that the dump's FORMAT is an interface ("no field may
# contain a tab or a newline, which tests/cli case 10 asserts by counting
# fields"). NOT tagged `pc3`: pcre2_check.c links the registry directly and
# never reads the rendered dump, so there is no path for it to see this — an
# arm added there would be a measured zero with no claim behind it.
SAB_ID="S18-tsv-empty"
SAB_FILE="src/parse/syntax_dump.c"
SAB_SUITES="reject registry cli"
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
