# S276 ([chkgaps] check-design closure) — G2 ADMITTED FOR AN UNANCHORED VM
# ROUTE: the generalized shape of K64's own defect, on a population K64's
# real bug never reaches.
#
# WHAT IT BREAKS. `req_route_one_attempt`'s VM arm (src/gen/emit_dfa.c)
# declines the necessary-byte pre-check only when `Job.start_anchor !=
# PCREC_SANCH_NONE` -- an anchored or `\G`-anchored route, which can try at
# most one start position. This plant drops that conjunct, so the VM arm
# admits ("one-attempt") EVERY VM route, anchored or not. K64 itself
# (docs/dev/known_issues.md) is the narrower defect this generalizes: it is
# already-broken for FRAMED, ANCHORED, one-attempt VM routes, because
# `req_route_one_attempt` never checks linearity either -- this plant is the
# same missing-conjunct SHAPE one level up, on the conjunct K64's own fix
# does NOT touch (the anchor test), so it is answer-detectable on a
# population independent of K64's own still-open fix.
#
# WHY THIS IS AN UNANCHORED WITNESS AND NOT K64's OWN PATTERN. An unanchored
# route may restart at every subject position, so admitting it as
# "one-attempt" removes the ONE mechanism (the whole-subject `memchr`) that
# used to prove NO-MATCH in a single bounded pass when the necessary byte is
# absent -- without it, the VM must try the nested-quantifier's own
# catastrophic cost at every start position, sharing one step budget across
# all of them (f3search_report.md's own finding: the counter is per-CALL,
# not per-attempt). `tests/codegen/run_prechecks.sh` §5.7 measured this
# exact pattern's UNANCHORED route as admission's positive control -- REQ_WHY
# reads "emitted" on the clean tree specifically BECAUSE it is unanchored --
# so this plant is that control's own failing direction. (§5.7, not §5.6:
# main's own K64 fix (lane k64fix) took §5.6 for its own narrower, ANCHORED
# witness while this lane was in flight; §5.6 and §5.7 are siblings, not a
# collision -- see the chkgaps/k64fix merge reconciliation report.)
SAB_ID="S276-precheck-g2-unanchored-admitted"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC="req_route_one_attempt's VM arm drops the Job.start_anchor != PCREC_SANCH_NONE conjunct and admits EVERY VM route as one-attempt, anchored or not -- so an unanchored, forced-VM, necessary-byte-bearing pattern loses its whole-subject memchr pre-check and must instead try a catastrophic-backtracking nested quantifier at every start position under one shared step budget"
SAB_DOC_FIGURE="MEASURED 2026-09-25 (lane chkgaps, solo single-row scratch run via tests/mech/run_sabotage_matrix.sh S276): DETECTED, reach:ok(1/1), prechecks:8fail/244pass. Section 5.6's own positive control flips from RX_REQ_WHY \"emitted\" to \"one-attempt\" and its no-'@' subject flips from exit 1 (nomatch, bounded) to a step give-up; the other 4 failures are the same missing conjunct reached through §5's own other witnesses (every VM-route pattern is now admitted regardless of anchoring). Read the current figure from a run."
SAB_REACH='"$PCREC" -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern "([a-zA-Z0-9._%+-]+)+@" && grep -q "^#define RX_REQ_WHY \"emitted\"" "$REACH_TMP/o.c" && grep -q "memchr(subject + search_from," "$REACH_TMP/o.c" && echo REACH-UNANCHORED-VM-EMITS'
SAB_REACH_EXPECT="REACH-UNANCHORED-VM-EMITS"
SAB_COUNT=1
SAB_BEFORE='static bool req_route_one_attempt(Ctx *cx)
{
    if (cx->job->fit.chosen == ENGM_VM)
        return cx->job->start_anchor != PCREC_SANCH_NONE;
    return cx->job->engine == PCREC_ENG_ATTEMPT &&
           dfa_interior_dead(cx->job->dfa.s1u);
}'
SAB_AFTER='static bool req_route_one_attempt(Ctx *cx)
{
    /* SABOTAGE S276: the VM arm admits EVERY VM route as one-attempt,
     * dropping the start_anchor conjunct -- an UNANCHORED route is no
     * longer bounded to one start position at all. */
    if (cx->job->fit.chosen == ENGM_VM)
        return true;
    return cx->job->engine == PCREC_ENG_ATTEMPT &&
           dfa_interior_dead(cx->job->dfa.s1u);
}'
