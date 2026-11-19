#!/usr/bin/env bash
# S3086 ([MEMFN] plan_frame.md 3.0b, row (T); lane b30b) -- NONE ANSWERS FRAME PART.
#
# WHAT IT BREAKS AND WHO CATCHES IT: a NONE ask answers a frame part (framed 1): the fixture comparing NONE's frame part to zero (memcmp from offsetof(mf_wreply, framed)) is red.
# The detector is tests/memfn/run_finder.sh's purity harness (arm_fixtures
# --purity, plain and, since 3.0b, the MF_TRACE fixture driver too); the
# population probe pins that run_finder.sh still runs the pass this row needs.
SAB_ID="S3086-none-answers-frame-part"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='a NONE ask answers a frame part (framed 1): the fixture comparing NONE'"'"'s frame part to zero (memcmp from offsetof(mf_wreply, framed)) is red'
SAB_DOC_FIGURE='Validated by plant at 3.0b (lane b30b, docs/dev/lanes/b30b_report.md), by hand on a copy of memfn/src: plain fx --purity 11 failed. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3086.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fx" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-ANCHORED 2026-11-16 (lane span4k, MF_SITE_ABI 30): reply_of writes the caller's rows
# and returns a verdict, and the decision's working state is a heap block per ask; intent unchanged.
# RE-ANCHORED 2026-11-16 (lane span4kfix, review r27 SEAM-1): the NONE ask writes its
# reply only after rows_hold; the plant follows that write. Intent unchanged.
SAB_BEFORE='        reply_of(d, out, rows);
        rc = 0;'
SAB_AFTER='        reply_of(d, out, rows);
        rc = 0;
        out->framed = 1;   /* SABOTAGE S3086 */'
