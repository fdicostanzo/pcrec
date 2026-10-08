#!/usr/bin/env bash
# S621 ([DEC-FALLBACK] S-I3, dec_fallback.md §4.4; drafted at B0, numbered at
# B1, lane decfbB1) -- the `emit-ir-auto` stream's `-fno-prefilter` arm is
# lost in plumbing, so T2's `forced-off` row (and row 6's SEL1 scope, reached
# only under that flag) is never listed by the B4 hard gate's stream.
# Detector (arm emitsweep): scripts/tests/emit_sweep.py.test (the arm's own
# tally and the per-token floor on `no-fno-prefilter`).
SAB_ID='S621-emit-ir-auto-no-prefilter-arm-lost'
SAB_FILE='scripts/emit_sweep.py'
SAB_SUITES='emitsweep'
SAB_DESC="emit_sweep's emit-ir-auto stream drops its -fno-prefilter arm: T2's forced-off listing token and the overflow-drop SEL1 scope go unswept"
SAB_DOC_FIGURE='B0 measured the plant at 3 self-test reds and a full-corpus TAG FLOOR red (docs/dev/lanes/decfbB0_report.md item 2); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S621.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='IR_AUTO_ARMS = ("", "-fno-prefilter", "-fprefilter", "-fno-prefilter-collapse")'
SAB_AFTER='IR_AUTO_ARMS = ("", "-fprefilter", "-fno-prefilter-collapse")   # SABOTAGE S621'
