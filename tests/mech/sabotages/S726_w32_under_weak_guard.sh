#!/usr/bin/env bash
# S726 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- the widest level's arm under a requirement one level too weak. Re-aimed at unit U2 (lane u2): the level's `needs` name the next-lower feature. DECLARED UNDETECTED: every target row that supplies the weaker feature also supplies the level's real one (the features column is each target's complete set, the kit manager's ruling), so the weak need admits exactly the same targets and no text moves. What would close it: a target row that supplies the weaker feature alone; G2 would then compile the 32-byte helpers in a region that lacks their feature.
SAB_ID='S726-w32-under-weak-guard'
SAB_FILE='memfn/src/levels.def'
SAB_SUITES='memfntargets g2simd'
SAB_DESC='the widest level needs only the next-lower feature: admitted at the same targets today, so nothing can see it'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S726. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=UNDETECTED
SAB_COUNT=1
SAB_BEFORE='"avx2", "imm'
SAB_AFTER='"avx", /* SABOTAGE S726 */ "imm'
