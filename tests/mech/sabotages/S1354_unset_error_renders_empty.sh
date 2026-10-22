# S1354 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: --unset=error renders an unset numbered group empty instead of refusing.
# Witness: the `unseterr` cell (`(a)|(b)` -> `[$1|$2]`, --unset=error): rc UNSET expected.
# Reach (K35): token S1354 (cell unseterr); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1354-unset-error-renders-empty"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='--unset=error renders an unset numbered group empty instead of refusing'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1354.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                        it->ref, uerr);'
SAB_AFTER='                        it->ref, 0 * uerr);   /* SABOTAGE S1354 */'
