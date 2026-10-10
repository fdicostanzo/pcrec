#!/usr/bin/env bash
# S741 ([MEMFN] R-13 follow-up, lane rankuse, 2026-10-09) -- the KB deny ignored: the cli case for --memfn=no-vrun-kb and G2's deny-kb class.
SAB_ID='S741-vrun-kb-deny-ignored'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='cli g2simd'
SAB_DESC='--memfn=no-vrun-kb does nothing: the second filter position is always read'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S741. docs/dev/lanes/rankuse_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (kit_opt_denied(x->site->opts, "vrun-kb")) return -1;'
SAB_AFTER='    if (0 && kit_opt_denied(x->site->opts, "vrun-kb")) return -1;   /* SABOTAGE S741 */'
