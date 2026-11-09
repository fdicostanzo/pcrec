#!/usr/bin/env bash
# S2994 -- [XARCH-DEV] unit U2 (request R-37; lane u2), LEVEL ADMISSION against the compiler
# (memfn/tests/check_targets.sh's admission control). THE 32-BYTE TARGET FORGETS A FEATURE IT SUPPLIES.
#
# Plant: memfn/src/targets.def's 32-byte target row drops the 16-byte level's one need from its
# features (its needs stay), the row as K0 wrote it: the kit then refuses the 16-byte level there, and
# the target renders its top rung alone (how the lane's own U3 preview first found it: `vrun@w32`
# without w16).
# Detectors (arm memfntargets): check_targets.sh's admission control (the compiler's own option for
# that need defines nothing new at the target, so the compiler supplies the need the table refuses)
# and targets_check.c's admission literals (the 32-byte target's kernel loses its w16 helper); since
# the kit manager's ruling (features are each target's complete supplied set) also the table check's
# features control (a feature the compiler enables there is not listed).
SAB_ID="S2994-targets-v3-drops-w16-feature"
SAB_FILE="memfn/src/targets.def"
SAB_SUITES="memfntargets"
SAB_DESC='the 32-byte target forgets a feature the compiler supplies there, so the kit refuses the 16-byte level at it'
SAB_DOC_FIGURE='MEASURED by lane u2, planted by hand in a scratch copy of the table (TARGETS_DEF; u2_report.md, Sabotage rows); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2994.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='sse,sse2,sse3'
SAB_AFTER='sse,sse3'
