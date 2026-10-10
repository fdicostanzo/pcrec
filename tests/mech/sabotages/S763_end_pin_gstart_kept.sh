#!/usr/bin/env bash
# S763 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- `end_pin` drops the `\G` decline (3), so `end_window` (its reader) clamps a `\G` pattern.
# Detector: the answer net's D family (`\Ga$|b$` at startpos 1) and tests/assertions' `\G` rows: the window clamp moves the startpos `\G` reads.
SAB_ID='S763-end-pin-gstart-kept'
SAB_FILE='src/facts/endwin.c'
SAB_SUITES='harness'
SAB_DESC='`end_pin` drops the `\G` decline (3), so `end_window` (its reader) clamps a `\G` pattern'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S763.'
SAB_HARNESS_TARGET='tests/assertions'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (gstart) return PCREC_EPIN_NONE;                   /* (3) */'
SAB_AFTER='    (void)gstart;   /* SABOTAGE S763: \G no longer declines the pin */'
