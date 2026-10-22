# S1360 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: a bare $name reads one byte, so `$gx` is $g then a literal x.
# Witness: the `greedyname` cell (`[$gx]` on `(?<g>b)`): bind MISSING_REF expected.
# Reach (K35): token - (cell greedyname); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1360-name-not-greedy"
SAB_FILE="src/parse/subst_template.c"
SAB_SUITES="subst"
SAB_DESC='a bare $name reads one byte, so `$gx` is $g then a literal x'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1360.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    while ((len = st_name_char(s, n, j, utf, false)) > 0) j += (size_t)len;'
SAB_AFTER='    while (0 && (len = st_name_char(s, n, j, utf, false)) > 0) j += (size_t)len;   /* SABOTAGE S1360 */'
