# S87 — [M6.2 WAVE E] THE `\K` WRITE IS NOT CHARGED TO THE TRAIL CAPACITY.
#
# THE THIRD OF THE WAVE'S THREE ROWS, AND THE ONLY ONE THE STRUCTURAL CHECKS
# CANNOT SEE. S85 guards where `caps[0][0]` is READ FROM and S86 whether the
# write can be TAKEN BACK; both fire `[M6.2-KRESET rule 1]` by name. This one
# guards whether the artifact was SIZED for the write, and `codegen` stays
# completely green under it — 56 pass, 0 fail, all four `[M6.2-KRESET]` checks
# included. The corpus is the only instrument in the tree that sees it.
#
# WHAT IT IS THE FAILING DIRECTION OF. Every other member of module
# `assertions` emits a test and costs `vm_cost` nothing. `\K` emits
# `<PREFIX>_SET(0, pos)`, which is a TRAIL ENTRY, so `vm_cost`'s A_KRESET arm
# must charge one — multiplied by the enclosing quantifier exactly as A_CAP's
# two writes are. The design note calls the construct "one line" (§6.2) and
# says nothing about capacity; this is the cost that hides behind that phrase.
#
# THE SABOTAGE returns the zero Cost, so `trail_frames` comes out short by one
# entry per `\K` on the deepest path. Nothing miscompiles and nothing is
# emitted differently — the artifact simply declares an array too small for
# the program beside it, and returns `PCREC_ERR_FRAMES` on a pattern it can
# match. That failure mode is why the row exists: an under-sized bound is not
# a wrong ANSWER, it is a REFUSAL to answer, and refusals are exactly what a
# corpus of matching cells is worst at noticing unless somebody wrote cells
# that reach the bound.
#
# MEASURED, and the shallow-vs-deep split is the point:
#
#     a\Kb                 declares 2 trail entries, sabotaged 1
#                          -> still compiles, still answers (1,2) on "ab".
#                          A one-write pattern fits anyway, so every cell in
#                          sections 1-3 of the corpus passes under this row.
#     (?:a\K){0,10}ab      declares 13 trail entries, sabotaged 3
#                          -> "ab" and "aaab" still answer; ELEVEN `a`s
#                          return `frames`. The subject has to exceed the
#                          repeat's count before the trail fills, so a
#                          subject chosen for length rather than for COUNT
#                          would pass here too.
#
# tests/assertions/kreset.rxt section 11 exists for this row and says so in
# its own header; without it the corpus failure count under this sabotage is
# 25 (section 4's loops alone, which reach the bound only incidentally) rather
# than 33, and the cells that fail would be there for a different reason.
#
# MEASURED through the CANONICAL DRIVER (`run_sabotage_matrix.sh S87`,
# 2026-08-19, tree 6ced17f): **codegen:0fail/56pass, corpus:33fail/563pass,
# kresetdiff:3fail/6pass -- DETECTED.** The 0-fail codegen column is the whole
# reason this row exists as a third one: the matrix CONFIRMS that all four
# [M6.2-KRESET] structural checks stay green, so the claim that this defect is
# invisible to them is the driver's measurement rather than the author's.
SAB_ID="S87-kreset-trail-uncharged"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness kresetdiff"
SAB_HARNESS_TARGET="tests/assertions/kreset.rxt"
SAB_DESC="vm_cost's A_KRESET arm returns the zero Cost instead of charging one trail entry, so an artifact's trail_frames is short by one per emitted \\K on the deepest path. Nothing is emitted differently and no answer changes -- the artifact returns PCREC_ERR_FRAMES on a pattern it can match: '(?:a\\K){0,10}ab' declares 3 trail entries where it needs 13 and answers 'frames' from eleven a's onward"
SAB_DOC_FIGURE="codegen:0fail/56pass,corpus:33fail/563pass,kresetdiff:3fail/6pass -- DETECTED (canonical matrix run, 2026-08-19). The 0fail codegen column is the row's point: all four [M6.2-KRESET] checks stay green"
SAB_COUNT=1
SAB_BEFORE='    case A_KRESET:
        c.trail = 1;
        return c;'
SAB_AFTER='    case A_KRESET:
        return c;   /* SABOTAGE S87 */'
