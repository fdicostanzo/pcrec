# S119 (design row S-BR16) — §5.3's DEFERRED VALIDITY CHECK IS SKIPPED.
#
# R32 C4 added this row because the first design had none for it, and the
# failure mode is the quietest in the family: A REFERENCE TO A NONEXISTENT
# GROUP IS SILENTLY ACCEPTED and then reads `PCREC_UNSET` forever. A pattern
# that should be PCRE2's error 115 becomes one that compiles cleanly and NEVER
# MATCHES.
#
# WHY THE CHECK IS DEFERRED AT ALL, and why that makes this row necessary
# rather than paranoid: rule 2 makes `\1`..`\9`'s VALIDITY a whole-pattern
# question (`\1(a)` compiles — the group is AFTER the escape), and the
# relative and by-name spellings need the final count and the complete set of
# declarations too. So the parser CANNOT refuse at the escape, and the only
# thing standing between "legal forward reference" and "reference to nothing"
# is this one end-of-parse pass.
#
# It also carries the `refs` arrays, so skipping it leaves `nrefs == 0` and
# the emitted chain has no arm at all — which is why the row's detector is
# both `octal.rxt`/`spellings.rxt`'s refusal cells and any pattern that should
# match.
SAB_ID="S119-deferred-validity-skipped"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness reject brefdiff"
SAB_HARNESS_TARGET="tests/backrefs"
SAB_DESC="pcrec_parse_info stops running the end-of-parse resolution pass, so a reference to a group the pattern never declares is accepted silently and every A_BREF is left with an EMPTY refs array. (a)\\2 compiles instead of raising the error-115-class diagnostic, and every backreference stops matching"
SAB_DOC_FIGURE="PREDICTED: the corpus RED across tests/backrefs; reject RED on the error-115 cells. Canonical figure owed from run_sabotage_matrix.sh S119."
SAB_COUNT=1
SAB_BEFORE='    return pcrec_bref_resolve(cx, a);'
SAB_AFTER='    return a;   /* SABOTAGE S119: nothing resolves, nothing refuses */'
