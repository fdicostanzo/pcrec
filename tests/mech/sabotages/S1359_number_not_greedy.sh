# S1359 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: a group number reads one digit, so `$12` is $1 then a literal 2.
# Witness: the `greedynum` cell (`$12` on `(b)`): the check MISSING_REF expected.
# Reach (K35): token - (cell greedynum); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1359-number-not-greedy"
SAB_FILE="src/parse/subst_template.c"
SAB_SUITES="subst"
SAB_DESC='a group number reads one digit, so `$12` is $1 then a literal 2'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1359.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    while (*i < n && st_digit((unsigned char)s[*i])) {'
SAB_AFTER='    if (*i < n && st_digit((unsigned char)s[*i])) {   /* SABOTAGE S1359 */'
