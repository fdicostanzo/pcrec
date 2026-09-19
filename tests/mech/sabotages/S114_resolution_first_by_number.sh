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
# sabotage would not show that the corpus DISCRIMINATES between them.#
# RE-AIMED 2026-09-18 (lane w2b, [REVW.2] wave 2 stage 3). The anchor's SECOND
# line was `char ns[144], ne[144];` -- the pair of hand-sized buffers the
# backreference chain wrote its two slot expressions into. Stage 3 retired
# them: `vm_slot_expr` now RETURNS arena-owned text, so the line is
# `const char *ns = vm_slot_expr(v, 2 * a->u.bref.refs[i]);` and the second
# declarator moved to its own line below. The PLANT and its INTENT are
# UNCHANGED -- the loop header, which is what this row truncates to its first
# member, is byte-identical and still at column 8 -- and the row was re-driven
# SOLO after the re-aim rather than assumed (see docs/dev/lanes/w2b_report.md).
SAB_ID="S114-resolution-first-by-number"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="dupnamesdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/dupnames.rxt"
SAB_DESC="The emitted else-if chain over a duplicated name's run is truncated to its FIRST member, so resolution becomes \"first by number\" unconditionally instead of \"first that is SET\". (?J)^(?:(?<a>x)|(?<a>y))\\k<a>\$ stops matching \"yy\"; every cell where the first member participates is unaffected"
SAB_DOC_FIGURE="PREDICTED: dupnamesdiff RED; the corpus RED on exactly the \"yy\" cell of dupnames.rxt's resolution block. Canonical figure owed from run_sabotage_matrix.sh S114."
SAB_COUNT=1
SAB_BEFORE='    for (int i = 0; i < a->u.bref.nrefs; i++) {
        const char *ns = vm_slot_expr(v, 2 * a->u.bref.refs[i]);'
SAB_AFTER='    for (int i = 0; i < 1 && i < a->u.bref.nrefs; i++) {   /* SABOTAGE S114 */
        const char *ns = vm_slot_expr(v, 2 * a->u.bref.refs[i]);'
