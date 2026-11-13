#!/usr/bin/env bash
# S3120 ([MEMFN] span_pick 3.0b, D27 finding F1; lane d27fix) -- THE PINNED RANKING IGNORES THE MEMBER'S TIE.
#
# WHAT IT BREAKS AND WHO CATCHES IT: translate ranks a pinned run's term under the art's tie again, not
# under the tie its run member was decided with. A verify-NO run's member keeps the stretch row whatever
# the lever, so under the test-only lever run-tie-left a lawful site whose two lightest exact positions
# tie ranks the left one first while C-pin holds the stop to the right one: the ranking's loud check
# refuses the define (D27 witness W1). No pcrec byte moves (pcrec states no lever). The detector is the
# D27 frame suite (tests/memfn/d27_frame/): its no_fenced_defect_refusal check on every lever site.
SAB_ID="S3120-pinned-rank-ignores-member-tie"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnd27frame"
SAB_DESC='translate ranks a pinned run under the art'"'"'s tie, not its member'"'"'s: under run-tie-left a lawful verify-NO site refuses its define through the ranking'"'"'s invariant (D27 finding F1)'
SAB_DOC_FIGURE='Validated by plant (lane d27fix, docs/dev/lanes/d27fix_report.md), by hand on a copy of the tree: D27_QUICK=1 tests/memfn/d27_frame/run.sh red. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3120.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (d->pinned) ro.tie = member_opts(d, &m->alt->spans[m->run]).tie;'
SAB_AFTER='        /* SABOTAGE S3120: the art'"'"'s tie for every ranking */'
