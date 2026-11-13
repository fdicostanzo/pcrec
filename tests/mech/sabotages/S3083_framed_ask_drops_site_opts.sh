#!/usr/bin/env bash
# S3083 ([MEMFN] plan_frame.md 3.0b, row (I); lane b30b) -- FRAMED ASK DROPS SITE OPTS.
#
# WHAT IT BREAKS AND WHO CATCHES IT: a framed ask's walks get a site copy with opts cleared: the fixture 'a framed ask on a REPORT site under no-window-search answers -1, as mf_define refuses' is red, and so is the T-FIND deny fixture under no-fd-d1 (search LIBC iff the define's text calls memchr).
# The detector is tests/memfn/run_finder.sh's purity harness (arm_fixtures
# --purity, plain and, since 3.0b, the MF_TRACE fixture driver too); the
# population probe pins that run_finder.sh still runs the pass this row needs.
SAB_ID="S3083-framed-ask-drops-site-opts"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='a framed ask'"'"'s walks get a site copy with opts cleared: the fixture '"'"'a framed ask on a REPORT site under no-window-search answers -1, as mf_define refuses'"'"' is red, and so is the T-FIND deny fixture under no-fd-d1 (search LIBC iff the define'"'"'s text calls memchr)'
SAB_DOC_FIGURE='Validated by plant at 3.0b (lane b30b, docs/dev/lanes/b30b_report.md), by hand on a copy of memfn/src: plain fx --purity 10 failed. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3083.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fx" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        !wf_plan_site(art, &heap, site, def, gphases, 1, d, w, L, fx, &r, &why)) {'
SAB_AFTER='        !wf_plan_site(art, &heap, ({ static mf_site c_; c_ = *site; c_.opts = NULL; &c_; }), def, gphases, 1, d, w, L, fx, &r, &why)) {   /* SABOTAGE S3083 */'
