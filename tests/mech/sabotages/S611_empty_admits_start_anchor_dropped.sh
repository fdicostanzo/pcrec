# S611 — [NULLABLE-ANCH] THE START HALF OF `empty_admits` DROPPED: an empty
# path that crosses only an END anchor reads as confined, so a one-sided
# pattern (`(\s+)*$`, empty at offset n of EVERY subject) is admitted to the
# exact hybrid prefilter the decline exists to refuse.
#
# THE PLANT: `pcrec_empty_masks_admit` (src/facts/widths.c) stops requiring
# `EM_S` — a mask of `EM_E` alone is treated like `EM_SE`. Answer-identical by
# construction (a prefilter is a filter, S206's argument), so no corpus cell
# can see it; the detector is `run_prefilter_collapse.sh`'s [anch] DECLINE
# twin `(\s+)*$`, whose stamps and `empty_admits` row both flip. Its admitted
# twin `^(\s+)*$` stays green, which is what says the plant moved the PREDICATE
# rather than the whole decline.
SAB_ID="S611-empty-admits-start-anchor-dropped"
SAB_FILE="src/facts/widths.c"
SAB_SUITES="pfcollapse"
SAB_DESC="[NULLABLE-ANCH] empty_admits stops requiring the start anchor: an empty path crossing only a non-multiline end anchor counts as confined, so '(\\s+)*\$' (empty at the end of every subject) is admitted to the exact hybrid prefilter -- answer-identical, seen only by the [anch] decline twin's stamps and listing row"
SAB_DOC_FIGURE="pfcollapse:1fail expected -- [anch] '(\\s+)*\$' stamps hybrid/selected/no where the decline is owed; every admitted [anch] row stays green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S611."
SAB_REACH_POP="tests/codegen/run_prefilter_collapse.sh|^for p in .* '[(][\\]s[+][)][*][$]'|1"
SAB_COUNT=1
SAB_BEFORE='    return (set & ~(1u << EM_SE)) != 0;'
SAB_AFTER='    return (set & ~((1u << EM_SE) | (1u << EM_E))) != 0;   /* SABOTAGE S611 */'
