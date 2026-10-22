# S1380 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: --subst ignores a pattern-compile option.
# Witness: run_subst_tests.sh's option loop (`-i`, `--engine=vm`, ... each refused with --subst).
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1380-subst-ignores-pattern-options"
SAB_FILE="cli/main.c"
SAB_SUITES="subst"
SAB_DESC='--subst ignores a pattern-compile option'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1380.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (memcmp(&d, &st->opt, sizeof d) != 0 || st->features || st->pattern_esc ||'
SAB_AFTER='    if (0 || st->features || st->pattern_esc ||   /* SABOTAGE S1380 */'
