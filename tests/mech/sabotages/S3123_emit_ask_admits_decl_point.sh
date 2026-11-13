#!/usr/bin/env bash
# S3123 ([MEMFN] span_pick 3.0b, D27 finding F3; lane d27fix) -- THE EMIT ASK ADMITS A DECLARATION POINT.
#
# WHAT IT BREAKS AND WHO CATCHES IT: an EMIT ask no longer refuses a `decl_point` 1 site. mf_emit uses
# the site straight after its define, before any mf_locals, so it always refuses one ("used before its
# mf_locals"); the ask answers 0. The detector is the D27 frame suite (tests/memfn/d27_frame/):
# refuse_iff_emit_refuses.
SAB_ID="S3123-emit-ask-admits-decl-point"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnd27frame"
SAB_DESC='an EMIT ask answers 0 on a decl_point 1 site, which mf_emit always refuses (no mf_locals before its use; D27 finding F3)'
SAB_DOC_FIGURE='Validated by plant (lane d27fix, docs/dev/lanes/d27fix_report.md), by hand on a copy of the tree: D27_QUICK=1 tests/memfn/d27_frame/run.sh red. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3123.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (use && site->decl_point) return -1;'
SAB_AFTER='    if (use && site->decl_point > 1) return -1;   /* SABOTAGE S3123 */'
