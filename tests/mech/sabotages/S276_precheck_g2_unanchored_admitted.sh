# S276 ([chkgaps] check-design closure; RE-ANCHORED at the chkgaps/k64fix
# merge, 2026-09-25, since K64's own fix (lane k64fix, landed concurrently)
# rewrote this exact function) — G2 ADMITTED FOR AN UNANCHORED VM ROUTE: the
# generalized shape of K64's own defect, on a population K64's fix does not
# touch.
#
# WHAT IT BREAKS. `req_route_one_attempt`'s VM arm (src/gen/emit_dfa.c)
# declines the necessary-byte pre-check only when `Job.start_anchor !=
# PCREC_SANCH_NONE` AND the attempt is linear (K64's own fix A added the
# second conjunct: an exact hybrid in front, or a frameless program) -- an
# anchored-and-linear route, which can try at most one start position and
# cannot blow its step budget per attempt. This plant drops BOTH conjuncts
# entirely, so the VM arm admits ("one-attempt") EVERY VM route, anchored or
# not, linear or not. K64 itself (docs/dev/known_issues.md, CLOSED) is the
# narrower defect this generalizes: it was broken for FRAMED, ANCHORED,
# non-linear VM routes only, on the ANCHOR conjunct's own population --
# this plant is the same missing-conjunct SHAPE one level up, on the
# UNANCHORED population K64's fix does NOT touch, so it is answer-detectable
# independent of which of the two conjuncts a future change narrows.
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
SAB_DESC="req_route_one_attempt's VM arm drops BOTH the Job.start_anchor != PCREC_SANCH_NONE conjunct and K64's own linearity conjunct, admitting EVERY VM route as one-attempt, anchored or not, linear or not -- so an unanchored, forced-VM, necessary-byte-bearing pattern loses its whole-subject memchr pre-check and must instead try a catastrophic-backtracking nested quantifier at every start position under one shared step budget"
SAB_DOC_FIGURE="MEASURED 2026-09-25 (lane chkgaps, re-anchored at the chkgaps/k64fix merge against the post-fix-A source; solo single-row scratch run via tests/mech/run_sabotage_matrix.sh S276): DETECTED, reach:ok(1/1). Section 5.7's own positive control flips from RX_REQ_WHY \"emitted\" to \"one-attempt\" and its no-'@' subject flips from exit 1 (nomatch, bounded) to a step give-up. Read the current prechecks figure from a run (was measured 8fail/244pass against the pre-merge, pre-§5.7 tree; the check population has since grown with §5.6/§5.7 both landing)."
SAB_REACH='"$PCREC" -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern "([a-zA-Z0-9._%+-]+)+@" && grep -q "^#define RX_REQ_WHY \"emitted\"" "$REACH_TMP/o.c" && grep -q "memchr(subject + search_from," "$REACH_TMP/o.c" && echo REACH-UNANCHORED-VM-EMITS'
SAB_REACH_EXPECT="REACH-UNANCHORED-VM-EMITS"
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
    /* SABOTAGE S276: the VM arm admits EVERY VM route as one-attempt,
     * dropping the start_anchor conjunct AND K64 fix A'"'"'s linearity
     * conjunct entirely -- an UNANCHORED route is no longer bounded to one
     * start position at all. */
    if (cx->job->fit.chosen == ENGM_VM)
        return true;
    return cx->job->engine == PCREC_ENG_ATTEMPT &&
           dfa_interior_dead(cx->job->dfa.s1u);
}'
