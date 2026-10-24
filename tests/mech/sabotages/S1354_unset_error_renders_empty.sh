# S1354 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: PCREC_SUBST_STRICT renders an unset group empty instead of refusing.
# Witness: the `unseterr` cell (`(a)|(b)` -> `[$1|$2]`, strict): rc UNSET expected.
# Reach (K35): token S1354 (cell unseterr); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1354-unset-error-renders-empty"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='PCREC_SUBST_STRICT renders an unset group empty instead of refusing'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1354.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    if (sl == -2) return (flags & PCREC_SUBST_STRICT) ? PCREC_SUBST_UNSET : 0;\n"'
SAB_AFTER='"    if (sl == -2) return 0;   /* SABOTAGE S1354 */\n"'
