#!/usr/bin/env bash
# S726 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- the widest level's arm under a requirement one level too weak. Re-aimed at unit U2 (lane u2): the level's `needs` name the next-lower feature, which no target row lists among its features, so the table no longer admits the level at its own target although the compiler supplies the feature there: the table check's admission control (memfntargets) reads a missing feature, and the 32-byte target's file loses its w32 helpers (g2simd).
SAB_ID='S726-w32-under-weak-guard'
SAB_FILE='memfn/src/levels.def'
SAB_SUITES='memfntargets g2simd'
SAB_DESC='the widest level needs the next-lower feature, which the table never lists: admission and the compiler disagree'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S726. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='MF_LEVEL(LV_X86_W32, "amd64", "avx2",'
SAB_AFTER='MF_LEVEL(LV_X86_W32, "amd64", "avx",   /* SABOTAGE S726 */'
