#!/usr/bin/env bash
# S762 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- `ew_walk` reads a multiline `$` as end-pinned (decline (4) dropped).
# Detector: the answer net's D family: `(?m)a$` on "a\nb" matches (0,1), which a walk from n never reaches.
SAB_ID='S762-end-pin-multiline-dollar'
SAB_FILE='src/facts/endwin.c'
SAB_SUITES='harness'
SAB_DESC='`ew_walk` reads a multiline `$` as end-pinned (decline (4) dropped)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S762.'
SAB_HARNESS_TARGET='tests/assertions/rev_end.rxt'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            return a->u.anch.multiline ? EW_NONE : EW_EOL;'
SAB_AFTER='            return EW_EOL;   /* SABOTAGE S762: (?m)$ pins */'
