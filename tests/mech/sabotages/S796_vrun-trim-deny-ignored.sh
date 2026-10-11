#!/usr/bin/env bash
# S796 ([MEMFN] R-14, lane r14b, 2026-10-11) -- the trim deny ignored: the cli case for --memfn=no-vrun-trim and G2's deny-trim class.
SAB_ID='S796-vrun-trim-deny-ignored'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='cli g2simd'
SAB_DESC='--memfn=no-vrun-trim does nothing: every candidate is verified over the trimmed run'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S796. docs/dev/lanes/r14b_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (kit_opt_denied(x->site->opts, "vrun-trim")) return 0;'
SAB_AFTER='    if (0 && kit_opt_denied(x->site->opts, "vrun-trim")) return 0;   /* SABOTAGE S796 */'
