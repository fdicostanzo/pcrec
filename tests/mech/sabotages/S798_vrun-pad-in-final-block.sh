#!/usr/bin/env bash
# S798 ([MEMFN] R-14 follow-up, lane r14p, 2026-10-11) -- the padded verify used in the final block too, where nothing holds the bytes past the run: an over-read past n. G2's SIMD family: its guard-page subjects (layout E, the subject's end a PROT_NONE page) fault and its ASan build reports the poisoned read; its verify rule also reads the text.
SAB_ID='S798-vrun-pad-in-final-block'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the final block verifies by the padded word: a candidate near n reads up to E bytes past the subject'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S798. docs/dev/lanes/r14p_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (vrun_verify(art, t, proven, np, 0, "        ", o)) return -1;'
SAB_AFTER='    if (vrun_verify(art, t, proven, np, (unsigned)e, "        ", o)) return -1;   /* SABOTAGE S798 */'
