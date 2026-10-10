#!/usr/bin/env bash
# S761 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- `ew_walk` pins an optional repeat (rmin == 0) by its body's view: `(?:a$)?` reads end-pinned.
# Detector: the answer net's D family: `(?:a$)?` on "b" must match empty at 0, the walk finds nothing there.
SAB_ID='S761-end-pin-optional-repeat'
SAB_FILE='src/facts/endwin.c'
SAB_SUITES='harness'
SAB_DESC='`ew_walk` pins an optional repeat (rmin == 0) by its body'\''s view: `(?:a$)?` reads end-pinned'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S761.'
SAB_HARNESS_TARGET='tests/assertions/rev_end.rxt'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (a->u.rep.rmin >= 1) { a = a->l; continue; }
            return EW_NONE;'
SAB_AFTER='            a = a->l; continue;   /* SABOTAGE S761: rmin == 0 keeps the pin */'
