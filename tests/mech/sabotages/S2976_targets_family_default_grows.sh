#!/usr/bin/env bash
# S2976 -- [XARCH-DEV] unit K0 (request R-36; lane k0). THE DISPATCH STEP TAKEN WITHOUT ITS VERDICT.
#
# Plant: memfn/src/targets.def's first family row's default list gains the 32-byte target (unit U5,
# which waits for a bench speed verdict, D144 add. 4). The list stays well-formed (both members of
# that family), so the table check's structural rules pass it.
# Detector: tests/memfn/targets_check.c (part 2 of tests/memfn/run_targets.sh, arm memfntargets): the
# family's default list is held to the design's literal, and the host default list with it.
SAB_ID="S2976-targets-family-default-grows"
SAB_FILE="memfn/src/targets.def"
SAB_SUITES="memfntargets"
SAB_DESC='a family default list grows by a member before its ruled step: only the literal control sees it'
SAB_DOC_FIGURE='MEASURED by lane k0, planted and reverted by hand in a scratch copy (k0_report.md, Sabotage); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2976.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='MF_FAM_X86_64,  "x86_64",  "x86-64")'
SAB_AFTER='MF_FAM_X86_64,  "x86_64",  "x86-64,x86-64-v3")'
