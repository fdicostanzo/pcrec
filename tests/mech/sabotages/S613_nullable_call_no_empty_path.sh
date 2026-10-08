# S613 — [NULLABLE-ANCH] A NULLABLE CALL CARRIES NO EMPTY PATH: the empty-path
# walk reads every `A_CALL` as non-nullable, ignoring the call graph's least
# fixpoint (K69). A pattern nullable only through a call then has an EMPTY
# mask set, which reads `empty_admits` false — the unsound direction (it would
# admit a prefilter that can dismiss nothing).
#
# THE DETECTOR is the E1 seal's own cross-check (`pf_check_e1`, src/facts/
# facts.c): a mask set must be nonempty exactly where `nullable` is, so the
# compile REFUSES with an internal error. `run_facts_checks.sh` [facts-e1]
# sees its two call-nullable witnesses (`(?(DEFINE)(?<g>a?))(?&g)` and the
# two-call chain) refused. A cross-check from the other walk
# (`pcrec_nullable`), not from the plant's own.
SAB_ID="S613-nullable-call-no-empty-path"
SAB_FILE="src/facts/widths.c"
SAB_SUITES="facts"
SAB_DESC="[NULLABLE-ANCH] the empty-path walk reads every subroutine call as having no empty path, so a pattern nullable only through a call gets an empty mask set (empty_admits false, the unsound direction) -- refused at the E2 seal by pf_check_e1's masks-vs-nullability cross-check"
SAB_DOC_FIGURE="facts:1fail expected -- [facts-e1] reports the call-nullable witnesses refused with 'internal error: [PATFACTS] the empty-path masks (0x0) disagree with nullability (yes)'. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S613."
SAB_COUNT=1
SAB_BEFORE='            return a->u.call.nonnullable ? 0 : acc;'
SAB_AFTER='            return 0;   /* SABOTAGE S613 */'
