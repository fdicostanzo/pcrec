# S1531 -- [M4-SUBST] module subst-extended (lane substext; docs/spec/subst_api.md
# §2¶7-¶14a, §4¶7-¶8, §4¶14, §4¶22).
#
# Plant: \u and \l leave the case region in force.
# Witness: the `t1` cell (`\Ua\ubc` renders `ABc`): the region survives and gives `ABC`.
# Reach (K35): token S1531; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1531-oneshot-keeps-region"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='\u and \l leave the case region in force'
SAB_DOC_FIGURE='Owed: lane substext queued this row (docs/dev/lanes/substext_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1531.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { EV(SUBST_EV_ONE_UPPER) | EV(SUBST_EV_ONE_LOWER), CW_ALWAYS,    CB_NONE,  CB_EVENT, CC_NONE },'
SAB_AFTER='    { EV(SUBST_EV_ONE_UPPER) | EV(SUBST_EV_ONE_LOWER), CW_ALWAYS,    CB_KEEP,  CB_EVENT, CC_NONE },   /* SABOTAGE S1531 */'
