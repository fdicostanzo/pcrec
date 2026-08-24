# S101 — [M6.4.4] THE FOLLOW CROSSES THE CUT AGAIN.
#
# This row reintroduces the TIER-1 MISCOMPILE the blinded D27 corpus found on
# `(?:aa|a)++ab`, and it is the only row in the matrix whose defect shipped:
# it was live in main from [M6.4.2]'s merge (69f3b93) until [M6.4.4].
#
# WHAT IT UNDOES. `vm_atomic` scopes `v->fmin` — the minimum width of what
# follows the GROUP — to zero while it emits the body, because `(?>X)` matches
# X's OWN FIRST SUCCESS and the follow must not influence which success that
# is. Restoring the caller's value is exactly the pre-fix emitter.
#
# WHY IT IS A LANGUAGE CHANGE AND NOT A LOST OPTIMISATION. The MRL machinery
# turns that number into a loop bound: the possessive rungs end their loop at
# the first position where "one more iteration PLUS THE FOLLOW" does not fit.
# For an UNCUT loop the shortcut is answer-preserving and `vm_opt_chain`'s own
# comment proves it — the body branch has no accepting leaf there, so the skip
# is the only survivor, AND THE SKIP IS STILL AVAILABLE TO RETREAT TO. Under a
# cut it is not. The loop stops at a position the greedy run would have walked
# past, and the follow then matches there: the UNCUT language, out of a
# possessive quantifier.
#
# `(?:aa|a)++ab` on "aaab" — libpcre2 10.46 and python3 `re` both NOMATCH,
# sabotaged pcrec (0,4).
#
# WHY THE PRE-[M6.4.4] CORPUS WAS GREEN ON IT, which is this row's real
# lesson. Every `cut` pattern in run_atomic_diff.sh had a follow whose first
# byte could NOT also start a body iteration (`(?:a|ab)*+c`). Under that
# disjointness the early exit lands where the follow cannot match either, so no
# answer moves and the defect is invisible. The family that sees it is a
# TWO-EXIT body under an OVERLAPPING follow — class `cut2`, 30 patterns across
# all five possessive rungs, added with the fix and carrying its own
# non-vacuity floor. A corpus is only as good as the shapes it contains, and
# this row exists so that stays measured rather than remembered.
SAB_ID="S101-follow-crosses-cut"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="atomicdiff harness codegen"
SAB_HARNESS_TARGET="tests/atomic_groups/possessive.rxt"
SAB_DESC="vm_atomic emits the atomic body with the caller's follow-min still in force, so the possessive rungs' MRL bound counts bytes the follow needs and ends the loop early. '(?:aa|a)++ab' on \"aaab\" then matches (0,4) where PCRE2 and python both give NO MATCH -- the UNCUT language out of a possessive quantifier. THE DEFECT THIS UNDOES SHIPPED: live in main from 69f3b93 to [M6.4.4]"
SAB_DOC_FIGURE="PREDICTED: atomicdiff RED on the cut2 family (30 patterns, all five rungs) and on its non-vacuity floor; harness RED on possessive.rxt's section 10 witnesses; codegen RED on the follow-barrier rule. Canonical figure owed from run_sabotage_matrix.sh S101."
# ANCHOR RE-HOMED 2026-08-23 ([M6.6.2] wave B+C), and the re-homing is itself
# the finding R33 V-7 predicted — arriving at THIS row rather than at the new
# one it warned about. The anchor was the single line `    v->fmin = 0;`. That
# was unique while `vm_atomic` was the only function scoping its body's follow;
# `vm_look` now carries the SAME TWO LINES (`lookaround_design.md` §3.2.1: the
# scoping is a property of the OVERLAP and not of the cut, so the lookaround
# needs it for a different reason and spells it identically), the anchor
# matched TWICE, and `replace.py` refused on the count — loudly, which is what
# it is for. The anchor now includes `vm_atomic`'s own signature, so
# `SAB_COUNT=1` is honest rather than lucky, and S132 — the lookaround's own
# scoping row — is anchored the same way for the same reason.
SAB_COUNT=1
SAB_BEFORE='static void vm_atomic(Vm *v, int entry, const Ast *a, int next)
{
    const char *sd = v->fdyn;
    long long   sf = v->fmin;
    v->fmin = 0;'
SAB_AFTER='static void vm_atomic(Vm *v, int entry, const Ast *a, int next)
{
    const char *sd = v->fdyn;
    long long   sf = v->fmin;
    v->fmin = sf;   /* SABOTAGE S101 */'
