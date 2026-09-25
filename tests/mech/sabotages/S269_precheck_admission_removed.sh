# S269 — [OPT-PRECHECK-ADMIT] G2 ADMISSION REMOVED (src/gen/emit_dfa.c,
# `req_route_one_attempt`): the predicate that answers "does this artifact's
# search route try exactly ONE start position" always says no, so the
# whole-window pre-check is emitted again in front of every `^`-anchored and
# `\G`-anchored route — the shape the bench measured at 20 ns -> 23 µs on
# `winpath-near-miss` and `email-nested-plus`
# (docs/dev/optloop/cycle1_ledger_reading.md §5, 29 regressing cells).
#
# THE PLANT RESTORES A CORRECT COMPILER, WHICH IS THE WHOLE DIFFICULTY OF THIS
# ROW AND ITS SIBLING S270. Neither decline can move an answer in either
# direction: the pre-check only ever returns the answer the engine below it
# then returns anyway, so a corpus arm sees NOTHING and a differential oracle
# sees nothing. `run_sabotage_matrix.sh`'s `harness` arm is listed anyway and
# is EXPECTED to stay green here; the detector is the structural one, and that
# asymmetry is the row's point rather than a defect in it.
#
# WHY IT IS NOT A DELETION OF THE CALL SITE. Removing
# `req_admit`'s own `if (req_route_one_attempt(cx))` line would leave the
# function unreferenced and the build would warn rather than compile clean,
# which is a different failure from the one under test. Emptying the PREDICATE
# leaves every caller, every stamp and every other rule exactly where they
# are, so what the suite sees is one rule's absence and nothing else.
SAB_ID="S269-precheck-admission-removed"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks harness"
SAB_DESC="the [OPT-PRECHECK-ADMIT] G2 ADMISSION rule is removed, so every artifact whose route runs exactly ONE attempt (the DFA's start_max row that is the literal 0 or search_from; the VM's RX_VM_START anchored/gstart) emits the whole-window memchr pre-check again in front of an exit that was already cheaper than the scan, which is the 29-cell regression class the batch-1 after-ledger attributed to this exact missing predicate"
SAB_DOC_FIGURE="tests/codegen/run_prechecks.sh is the detector and names the rule directly: section 5.1 reports the four one-attempt witnesses stamping RX_REQ_WHY 'emitted' where 'one-attempt' is expected, 5.1b reports the pre-check back in the file on each of them, 5.2 reports each witness no longer reaching the rule, 5.4 reports the <string.h> include returning to an artifact with no other memchr customer, and 5.5's G2 population floor drops to 0. Measured on the clean tree at 267 passed / 0 failed (258 before K65 added §5.7, 250 before K64 added §5.6). The harness arm is expected to stay GREEN: the decline moves no answer in either direction, which is exactly why this row exists. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S269."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree a
# `^`-anchored pattern with a necessary byte DECLINES, stamping the reason and
# emitting no pre-check. Both halves are asserted, because a later change that
# kept the stamp and moved the emission must read UNREACHED and not green.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "^abc$" && grep -q "^#define RX_REQ_WHY \"one-attempt\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_BYTE \"98\"" "$REACH_TMP/o.c" && ! grep -q "memchr(subject + search_from," "$REACH_TMP/o.c" && echo REACH-ADMISSION-DECLINES-ONE-ATTEMPT'
SAB_REACH_EXPECT="REACH-ADMISSION-DECLINES-ONE-ATTEMPT"
# [K64 re-anchor, lane k64fix, 2026-09-25] the VM arm gained its linearity
# conjunct (an exact hybrid in front, or a frameless program); the plant and
# its intent — the predicate always says no — are unchanged, and §5.6's
# one-attempt rows (the auto-route hybrid, the frameless forced VM) now fail
# under it beside §5.1/5.2's. Its K64 rows expect "emitted" and stay green.
SAB_COUNT=1
SAB_BEFORE='static bool req_route_one_attempt(Ctx *cx)
{
    if (cx->job->fit.chosen == ENGM_VM)
        return cx->job->start_anchor != PCREC_SANCH_NONE &&
               ((cx->job->fit.prefilter && !cx->job->fit.prefilter_collapsed) ||
                cx->job->vm_frameless);
    return cx->job->engine == PCREC_ENG_ATTEMPT &&
           dfa_interior_dead(cx->job->dfa.s1u);
}'
SAB_AFTER='static bool req_route_one_attempt(Ctx *cx)
{
    (void)cx;
    return false;   /* SABOTAGE S269: the G2 admission rule removed */
}'
