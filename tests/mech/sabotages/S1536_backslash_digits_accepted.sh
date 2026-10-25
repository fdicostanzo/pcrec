# S1536 -- [M4-SUBST] module subst-extended (lane substext; docs/spec/subst_api.md
# §2¶7-¶14a, §4¶7-¶8, §4¶14, §4¶22).
#
# Plant: a backslash with two or more digits is read as \1-\9 then digits instead of refused.
# Witness: tests/subst/run_subst_tests.sh section 2 extended refusals (`\10`, `a\101`, `\81` at their offsets): they compile.
# Reach (K35): token - (section 2 refusal rows, no cell); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1536-backslash-digits-accepted"
SAB_FILE="src/parse/subst_template.c"
SAB_SUITES="subst"
SAB_DESC='a backslash with two or more digits is read as \1-\9 then digits instead of refused'
SAB_DOC_FIGURE='Owed: lane substext queued this row (docs/dev/lanes/substext_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1536.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (j < n && st_digit((unsigned char)s[j]))'
SAB_AFTER='        if (0 && j < n && st_digit((unsigned char)s[j]))   /* SABOTAGE S1536 */'
