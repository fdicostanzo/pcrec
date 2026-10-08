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
SAB_BEFORE='        (has_var ? pcrec_fact_nullable(cx) : pcrec_fact_empty_admits(cx)) &&'
SAB_AFTER='        pcrec_fact_nullable(cx) &&   /* SABOTAGE S612 */'
