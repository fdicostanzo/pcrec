#!/usr/bin/env bash
# S3087 ([MEMFN] plan_frame.md 3.0b, row (U); lane b30b) -- EMIT WALKS DEFINE ONLY.
#
# WHAT IT BREAKS AND WHO CATCHES IT: an EMIT ask walks Table E under DEFINE only: on the fixture site mf_define renders on E-stmt (PF memchr) and mf_emit on E-find (the PF row declines its on_miss at USE), the EMIT ask answers mf_define's row and is red.
# The detector is tests/memfn/run_finder.sh's purity harness (arm_fixtures
# --purity, plain and, since 3.0b, the MF_TRACE fixture driver too); the
# population probe pins that run_finder.sh still runs the pass this row needs.
SAB_ID="S3087-emit-walks-define-only"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='an EMIT ask walks Table E under DEFINE only: on the fixture site mf_define renders on E-stmt (PF memchr) and mf_emit on E-find (the PF row declines its on_miss at USE), the EMIT ask answers mf_define'"'"'s row and is red'
SAB_DOC_FIGURE='Validated by plant at 3.0b (lane b30b, docs/dev/lanes/b30b_report.md), by hand on a copy of memfn/src: plain fx --purity 2 failed. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3087.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fx" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                              call == MF_WCALL_EMIT ? MF_PH_DEFINE | MF_PH_USE : MF_PH_DEFINE,'
SAB_AFTER='                              MF_PH_DEFINE,   /* SABOTAGE S3087 */'
