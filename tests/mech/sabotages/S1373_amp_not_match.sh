# S1373 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: `$&` is not the match.
# Witness: cells `amp` and `prepost`; reach token `amp`.
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1373-amp-not-match"
SAB_FILE="src/parse/subst_template.c"
SAB_SUITES="subst"
SAB_DESC='`$&` is not the match'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1373.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    case '\''&'\'':  return SUBST_GROUP;      /* the match: `$0` */'
SAB_AFTER='    case '\''&'\'':  return SUBST_LIT;   /* SABOTAGE S1373 */'
