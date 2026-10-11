#!/usr/bin/env bash
# S799 ([MEMFN] R-14 follow-up, lane r14p, 2026-10-11) -- the pad deny ignored: the cli case for --memfn=no-vrun-pad and G2's deny-pad class.
SAB_ID='S799-vrun-pad-deny-ignored'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='cli g2simd'
SAB_DESC='--memfn=no-vrun-pad does nothing: the main path always verifies by the padded word'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S799. docs/dev/lanes/r14p_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (kit_opt_denied(x->site->opts, "vrun-pad")) return 0;'
SAB_AFTER='    if (0 && kit_opt_denied(x->site->opts, "vrun-pad")) return 0;   /* SABOTAGE S799 */'
