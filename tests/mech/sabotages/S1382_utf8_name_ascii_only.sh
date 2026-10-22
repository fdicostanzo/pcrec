# S1382 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: a utf8 template's name takes no character >= 0x80.
# Witness: run_subst_tests.sh's utf8 name rows (`${é}`, `$éx1` compile to a named row).
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1382-utf8-name-ascii-only"
SAB_FILE="src/parse/subst_template.c"
SAB_SUITES="subst"
SAB_DESC='a utf8 template'\''s name takes no character >= 0x80'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1382.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return st_in_prop("L", cp) || (!first && st_in_prop("ND", cp)) ? len : 0;'
SAB_AFTER='    return 0 && (st_in_prop("L", cp) || (!first && st_in_prop("ND", cp))) ? len : 0;   /* SABOTAGE S1382 */'
