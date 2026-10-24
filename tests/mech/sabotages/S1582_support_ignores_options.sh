# S1582 -- [M4-SUBST] lane substr1fix (review 2026-10-24 r1 subst, CHK-7;
# docs/spec/subst_api.md §10¶2).
#
# Plant: --emit-support ignores every option (its presence refusal is dropped).
# Witness: cli_option_census.py (every option --help and --list-axes document,
# each refused with --emit-support by its presence).
SAB_ID="S1582-support-ignores-options"
SAB_FILE="cli/main.c"
SAB_SUITES="subst"
SAB_DESC='--emit-support ignores an option'
SAB_DOC_FIGURE='Owed: lane substr1fix queued this row (docs/dev/lanes/substland_report.md, substr1fix STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1582.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (unadmitted || st->nfiles) {'
SAB_AFTER='    if (st->nfiles) {   /* SABOTAGE S1582 */'
