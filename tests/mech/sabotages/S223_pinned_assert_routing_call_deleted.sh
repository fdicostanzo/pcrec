# S223 ([OPT-5] STEP 2, r51fix item 1) — THE P0 ROUTING ASSERTION'S ONE CALL
# SITE IS DELETED; THE FUNCTION DEFINITION IS LEFT AS DEAD CODE.
#
# WHAT IT BREAKS. `start_pinned_assert_routing` (src/gen/emit_dfa.c:4482) is
# the compiler-side guard for axis J's P0 premise ("ENG_UNANCH's s0 is the
# right state at search_from == 0") and for P3's LIVENESS conjunct, which
# this file's own header (emit_dfa.c:4475-4481) says has NO SABOTAGE WITNESS
# and cannot currently have one — the note's §5.6b derives that the
# P3-discriminating population looks EMPTY on ENG_UNANCH, so an assertion
# that needs no witness (its firing IS the finding) is the correct
# instrument. It has exactly ONE call site, emit_dfa.c:5123, inside axis J's
# own dispatch:
#
#     if (!pinned) dfa_form_derive(cx, &job->rdfa, &us, &dfa_dir_reverse, &rev);
#     else         start_pinned_assert_routing(cx, &job->dfa, job->dfa.s0);
#
# This plant deletes that call and nothing else. The function definition,
# its two ctx_fail messages and every other reader of its name are
# untouched — so a check that greps only for the IDENTIFIER
# `start_pinned_assert_routing`, or for its message text, still finds all
# three and reports the guard intact while the guard has stopped running at
# all.
#
# ================== WHY THIS ROW EXISTS (r51 finding 1) ==================
#
# `tests/codegen/run_search_pinned.sh` §7 was, before this row, exactly that
# vacuous check: three `grep -q` calls against the DEFINITION's name and
# message text, never against the CALL. r51check's finding: "Deleting the
# call and leaving the definition as dead code passes vacuously; and the
# file's own header says the liveness clause has no sabotage witness, so §7
# is its ONLY guard." §7 now carries a FOURTH grep, anchored on the call's
# own expression shape (`start_pinned_assert_routing(cx,`, which the
# DEFINITION'S signature — `(Ctx *cx, const Dfa *fd, int fs)` — never
# matches, since its own parameter spells the type: `(Ctx *cx,` not `(cx,`).
# This row is the row that fourth grep exists to catch, and the reverse
# tripwire the guard lacked before it.
#
# THE FAILURE MODE THIS PLANT STANDS IN FOR IS NOT AN ANSWER CHANGING TODAY
# — the assertion never fires on this corpus (S219's own measurement: zero
# P3 evaluations on 2,850 patterns across three axes) — it is the SAFETY NET
# for a machine shape nobody can currently build going silently unmonitored.
# No `.rxt` cell, no differential and no answer-identity sweep can see a
# deleted safety net whose alarm has never sounded; only a check that reads
# the wiring can.
SAB_ID="S223-pinned-assert-routing-call-deleted"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="searchpinned"
SAB_DESC="The start-pinned search's P0/P3 routing assertion (start_pinned_assert_routing) has its ONE call site deleted from axis J's dispatch; the function definition and its ctx_fail messages are left untouched as dead code. No answer moves anywhere in the tree -- the assertion never fires on this corpus (S219's own measurement) -- what is lost is the compiler-side guard against a future engine-selection change routing a machine past P0's or P3's premise without the elision noticing"
SAB_DOC_FIGURE="MEASURED 2026-09-03 (r51fix item 1, solo mech run, tree 26644f50edcafbceb056616650f6cca2f80f4d89): DETECTED, unexpected: 0 -- reach:ok(1/1), searchpinned:1fail/16pass. The single failure is §7's wiring grep (\`start_pinned_assert_routing(cx,\` finds no match); the other 16 checks in the file stay green, confirming no answer moves and that §7 was this row's only guard."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree the
# call-site expression is present in the emitter's own routing dispatch, not
# only in the function's definition line (whose signature spells the
# parameter as \`Ctx *cx\`, never \`cx,\` alone) -- the same distinction §7's
# fourth grep makes.
SAB_REACH='grep -q "start_pinned_assert_routing(cx," "$TREE/src/gen/emit_dfa.c" && echo REACH-CALL-SITE-PRESENT'
SAB_REACH_EXPECT="REACH-CALL-SITE-PRESENT"
SAB_COUNT=1
SAB_BEFORE='    else         start_pinned_assert_routing(cx, &job->dfa, job->dfa.s0);'
SAB_AFTER='    else         { /* SABOTAGE S223: the P0/P3 routing assertion CALL is
     * deleted here. The function definition below is untouched and becomes
     * dead code -- the wiring grep in run_search_pinned.sh section 7 is the
     * only guard that can see this. */ }'
