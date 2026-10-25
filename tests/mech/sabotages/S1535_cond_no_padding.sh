# S1535 -- [M4-SUBST] module subst-extended (lane substext; docs/spec/subst_api.md
# §2¶7-¶14a, §4¶7-¶8, §4¶14, §4¶22).
#
# Plant: a conditional stores no padding, so its shorter text breaks the fixed stride.
# Witness: the `k1`/`k2`/`k3`/`k19` cells (texts of different piece counts): the stride breaks and the output with it.
# Reach (K35): token S1535; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1535-cond-no-padding"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='a conditional stores no padding, so its shorter text breaks the fixed stride'
SAB_DOC_FIGURE='Owed: lane substext queued this row (docs/dev/lanes/substext_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1535.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!n) return;'
SAB_AFTER='    return;   /* SABOTAGE S1535 */'
