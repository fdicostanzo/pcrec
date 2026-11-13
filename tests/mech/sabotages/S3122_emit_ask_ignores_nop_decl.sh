#!/usr/bin/env bash
# S3122 ([MEMFN] span_pick 3.0b, D27 finding F2; lane d27fix) -- THE EMIT ASK IGNORES THE USE'S NOP-DECLARE REFUSAL.
#
# WHAT IT BREAKS AND WHO CATCHES IT: an EMIT ask no longer applies the refusal the statement frames
# (the window family's and the generic row's) make at their use: a NOP ASSIGN site whose one-call hooks
# declare the result. The ask answers 0 where mf_emit refuses ("a NOP ASSIGN cannot declare its
# result"). The detector is the D27 frame suite (tests/memfn/d27_frame/): refuse_iff_emit_refuses.
SAB_ID="S3122-emit-ask-ignores-nop-decl"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnd27frame"
SAB_DESC='an EMIT ask answers 0 on a NOP ASSIGN site whose hooks declare the result, where mf_emit refuses at its use (D27 finding F2)'
SAB_DOC_FIGURE='Validated by plant (lane d27fix, docs/dev/lanes/d27fix_report.md), by hand on a copy of the tree: D27_QUICK=1 tests/memfn/d27_frame/run.sh red. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3122.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!kit_nop_decl(s, h)) return 0;'
SAB_AFTER='    if (!kit_nop_decl(s, h) || ren) return 0;   /* SABOTAGE S3122 */'
