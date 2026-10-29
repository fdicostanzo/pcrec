# S1503 -- [M4-SUBST] (lane substb2; docs/design/replace_design.md §R4,
# docs/spec/subst_api.md §10¶7).
#
# Plant: replace-all returns 0, not the match count.
# Witness: every LIMIT-all out cell's `ra`, `size` and `exact` arms want the substitution count.
# Reach (K35): token count; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1503-replace-all-count-zero"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='replace-all returns 0, not the match count'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1503.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    return count > 2147483647u ? 2147483647 : (int)count;\n"'
SAB_AFTER='"    return 0;   /* SABOTAGE S1503 */\n"'
