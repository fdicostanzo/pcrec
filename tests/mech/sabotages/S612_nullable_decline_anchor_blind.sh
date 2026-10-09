# S612 — [NULLABLE-ANCH] THE DECLINE READS BARE NULLABILITY AGAIN: the
# shipped compiler of the day before this row. Every both-anchored nullable
# pattern loses its exact hybrid prefilter, and the VM partitions a near-miss
# run exponentially until its step budget gives up.
#
# THE PLANT: `lang_nullable_declinable` (src/opt/select_engine.c) reads
# `pcrec_fact_nullable` on every pattern, not only on a `${...}` one. Unlike
# S611 this one IS answer-visible: tests/base/nullable_anch.rxt's two GIVE-UP
# CELLS (`^(([a-z]+)*)+$` on 17 letters + `!`, `^(\s+)*$` on 32 blanks + `x`)
# expect `nomatch` and get PCREC_ERR_STEPS (~2 s each). The [anch] admit rows
# red too, on their stamps.
SAB_ID="S612-nullable-decline-anchor-blind"
SAB_FILE="src/opt/select_engine.c"
SAB_SUITES="harness pfcollapse"
SAB_HARNESS_TARGET="tests/base/nullable_anch.rxt"
SAB_DESC="[NULLABLE-ANCH] the prefilter decline reads bare nullability again, so a nullable pattern whose every empty path crosses ^ and \$ is declined its exact hybrid prefilter -- the near-miss give-up cells of tests/base/nullable_anch.rxt read PCREC_ERR_STEPS instead of nomatch, and the [anch] admit rows' stamps revert to declined-nullable-default"
SAB_DOC_FIGURE="harness:2fail (the two give-up cells) and pfcollapse:6fail (every [anch] admit row) expected. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S612."
SAB_REACH_POP="tests/base/nullable_anch.rxt|^# THE GIVE-UP CELL|2"
SAB_COUNT=1
# [DEC-FALLBACK] B4 (lane decfbB4, 2026-10-08) RE-AIMED, INTENT RE-VERIFIED.
# The `has_var` ternary is gone: T2's `nullable-exact` row (row 4) reads
# `empty_admits` where the ternary's non-variable arm did (design §4.4
# S-T2b). The plant reads bare nullability there. Narrower than the old
# plant by row 5 (`nullable-collapsed`, the rung scope), which keeps
# `empty_admits`; the give-up cells and the [anch] admit rows are all
# un-rung compiles, row 4's scope.
# [DEC-VAR-ATTRIB] (lane decattr, 2026-10-09) RE-ANCHORED, INTENT RE-VERIFIED:
# the `!pfa_var(s)` conjunct went with var-nullable (the var row precedes
# this one), the plant is unchanged.
SAB_BEFORE='    return pfa_default_scope(s) && pcrec_fact_empty_admits(s->cx);'
SAB_AFTER='    return pfa_default_scope(s) && pcrec_fact_nullable(s->cx);   /* SABOTAGE S612 */'
