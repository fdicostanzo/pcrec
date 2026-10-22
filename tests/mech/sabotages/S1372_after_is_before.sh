# S1372 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: `$'` parses as `$``.
# Witness: cell `prepost` (pcre2's `$'` is the suffix); reach token `after`.
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1372-after-is-before"
SAB_FILE="src/parse/subst_template.c"
SAB_SUITES="subst"
SAB_DESC='`$'\''` parses as `$``'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1372.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    case '\''\'\'''\'': return SUBST_AFTER;'
SAB_AFTER='    case '\''\'\'''\'': return SUBST_BEFORE;   /* SABOTAGE S1372 */'
