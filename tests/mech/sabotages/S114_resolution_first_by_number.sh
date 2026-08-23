# S114 (design row S-BR9) — §8.3's RESOLUTION TAKES THE FIRST BY NUMBER RATHER
# THAN THE FIRST THAT IS SET.
#
# ONE OF FOUR CANDIDATE RULES the design's eighteen cells were designed to
# separate, and it is the most plausible of them: the run IS in ascending
# number, so "take the first" is one dropped test away from correct.
#
# THE CELL THAT KILLS IT, and it is exactly one:
# `(?J)^(?:(?<a>x)|(?<a>y))\k<a>$` on "yy" MATCHES, with group 1 UNSET and
# group 2 = (0,1). Under this sabotage the chain reads group 1's unset pair,
# stops there, and the reference fails. Every cell where the FIRST member
# participates still passes.
#
# S114 AND S113 ARE SEPARATE ROWS ON PURPOSE (design §11.4's closing note):
# each is a plausible implementation, each passes the majority of the corpus,
# and each is caught by exactly one cell. A single "the rule is wrong"
# sabotage would not show that the corpus DISCRIMINATES between them.
SAB_ID="S114-resolution-first-by-number"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="dupnamesdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/dupnames.rxt"
SAB_DESC="The emitted else-if chain over a duplicated name's run is truncated to its FIRST member, so resolution becomes \"first by number\" unconditionally instead of \"first that is SET\". (?J)^(?:(?<a>x)|(?<a>y))\\k<a>\$ stops matching \"yy\"; every cell where the first member participates is unaffected"
SAB_DOC_FIGURE="PREDICTED: dupnamesdiff RED; the corpus RED on exactly the \"yy\" cell of dupnames.rxt's resolution block. Canonical figure owed from run_sabotage_matrix.sh S114."
SAB_COUNT=1
SAB_BEFORE='        for (int i = 0; i < a->u.bref.nrefs; i++) {
            char ns[144], ne[144];'
SAB_AFTER='        for (int i = 0; i < 1 && i < a->u.bref.nrefs; i++) {   /* SABOTAGE S114 */
            char ns[144], ne[144];'
