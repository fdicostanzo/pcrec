# S1539 -- [M4-SUBST] module subst-extended (lane substext; docs/spec/subst_api.md
# §2¶7-¶14a, §4¶7-¶8, §4¶14, §4¶22).
#
# Plant: an all-ASCII case-forcing template binds no encoding.
# Witness: the `encbind` cell (`\U$1` compiled under byte, used with a utf8 rx): the check must refuse it MISMATCH (subst_api.md §2¶5).
# Re-aimed by lane substr1fix (review TPL-1 moved the binding decision into
# the parser's st_case; same intent: case forcing binds no encoding).
# Reach (K35): token S1539; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1539-case-template-binds-any"
SAB_FILE="src/parse/subst_template.c"
SAB_SUITES="subst"
SAB_DESC='an all-ASCII case-forcing template binds no encoding'
SAB_DOC_FIGURE='Owed: lane substext queued this row (docs/dev/lanes/substext_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1539.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    t->enc_bound = true;'
SAB_AFTER='    (void)0;   /* SABOTAGE S1539 */'
