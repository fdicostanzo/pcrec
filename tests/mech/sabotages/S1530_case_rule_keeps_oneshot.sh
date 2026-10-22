# S1530 -- [M4-SUBST] module subst-extended (lane substext; docs/spec/subst_api.md
# §2¶7-¶14a, §4¶7-¶8, §4¶14, §4¶22).
#
# Plant: the case table first row keeps a pending one-shot when \U or \L replaces a region.
# Witness: the `t3` cell of tests/subst-extended/cells.tsv (`\u\U\Lab` renders `ab`, libpcre2 10.46): the one-shot survives and gives `Ab`.
# Reach (K35): token S1530; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1530-case-rule-keeps-oneshot"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the case table first row keeps a pending one-shot when \U or \L replaces a region'
SAB_DOC_FIGURE='Owed: lane substext queued this row (docs/dev/lanes/substext_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1530.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { EV(SUBST_EV_UPPER) | EV(SUBST_EV_LOWER),         CW_REGION,    CB_EVENT, CB_NONE,  CC_NONE },'
SAB_AFTER='    { EV(SUBST_EV_UPPER) | EV(SUBST_EV_LOWER),         CW_REGION,    CB_EVENT, CB_KEEP,  CC_NONE },   /* SABOTAGE S1530 */'
