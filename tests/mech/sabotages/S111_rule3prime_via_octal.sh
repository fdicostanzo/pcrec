# S111 (design row S-BR8b) — AN 8/9-LED DIGIT RUN IS ROUTED THROUGH THE OCTAL
# BRANCH.
#
# R32 E3, as a row. Rule 3 as the first design stated it was INCOMPLETE, and
# the gap is structural rather than a missing cell: `8` and `9` are NOT OCTAL
# DIGITS, so for a run beginning with one of them the "re-read as octal"
# branch consumes ZERO digits and produces nothing at all. PCRE2 reads the
# whole DECIMAL number instead — `\81` is a reference to group 81, error 115
# below that and legal at 81 groups, measured cell by cell.
#
# SO THE FAILURE IS A SILENT MIS-PARSE, not an error: the octal branch takes
# the selector digit `8` as a value of 8, which is not even an octal digit,
# and the pattern quietly matches a different language.
#
# It is a SEPARATE ROW from S110 on purpose: each is a plausible
# implementation, each passes the majority of `octal.rxt`, and each is caught
# by exactly one block. A single "the rule is wrong" sabotage would not show
# that the corpus DISCRIMINATES between them.
SAB_ID="S111-rule3prime-via-octal"
SAB_FILE="src/parse/mod_backrefs.c"
SAB_SUITES="harness brefdiff"
SAB_HARNESS_TARGET="tests/backrefs/octal.rxt"
SAB_DESC="A digit run beginning 8 or 9 falls into rule 3 instead of rule 3', so it takes the OCTAL re-read -- a branch that cannot consume a non-octal leading digit. \\81 stops being a decimal reference to group 81 and becomes a mis-parse; the failure is silent, because the octal branch produces a character rather than an error"
SAB_DOC_FIGURE="PREDICTED: the corpus RED on octal.rxt's rule-3' block only. Canonical figure owed from run_sabotage_matrix.sh S111."
SAB_COUNT=1
SAB_BEFORE='    if (runlen == 1 || d0 >= 8) {'
SAB_AFTER='    if (runlen == 1) {   /* SABOTAGE S111: 8/9-led runs fall to rule 3 */'
