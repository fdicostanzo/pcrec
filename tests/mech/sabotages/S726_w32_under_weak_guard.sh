#!/usr/bin/env bash
# S726 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- the widest level's arm under a requirement one level too weak. Re-aimed at unit U2 (lane u2): the level's `needs` name the next-lower feature. Admission alone cannot see it (every target row that supplies the weaker feature also supplies the real one), so it was UNDETECTED until [XARCH-NEEDSOK] (lane kclose2, 2026-11-10): memfn/tests/check_targets.sh compiles each level's rendered helpers at the check's floor plus each declared need, and the widest level's helpers fail to compile under the weaker need.
SAB_ID='S726-w32-under-weak-guard'
SAB_FILE='memfn/src/levels.def'
SAB_SUITES='memfntargets'
SAB_DESC='the widest level needs only the next-lower feature: admitted at the same targets, but its rendered helpers do not compile under the weaker need (a designed compile-time catch, [MECH-NOCOMPILE] COMPILE-CATCH: memfntargets compiles each level under its declared needs)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S726. docs/dev/lanes/kclose2_report.md carries the hand-plant run.'
SAB_EXPECT=COMPILE-CATCH
SAB_COUNT=1
SAB_BEFORE='"avx2", MF_INC_LEVEL_W32'
SAB_AFTER='"avx", /* SABOTAGE S726 */ MF_INC_LEVEL_W32'
