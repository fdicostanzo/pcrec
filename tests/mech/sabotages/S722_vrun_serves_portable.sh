#!/usr/bin/env bash
# S722 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- the SIMD layer renders where it must not. Re-aimed at unit U2 (lane u2): the layer is the art's TARGET, no longer bit 0 of the policy word, so the plant is the w16 row serving a target that does not admit its level (the portable target among them): G2's neg-portable class (an art stating the portable target) renders SIMD, and the generic target's file holds w16 helpers.
SAB_ID='S722-vrun-serves-portable'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the w16 vrun row serves every target, so the portable target (-fno-memfn-simd) renders SIMD text'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S722. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=',  /* a target admitting w16 */'
SAB_AFTER=' | CM_NO_LEVEL(0),  /* SABOTAGE S722: serves NO_w16 too */'
