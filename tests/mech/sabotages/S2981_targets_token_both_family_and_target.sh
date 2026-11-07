#!/usr/bin/env bash
# S2981 -- [XARCH-DEV] unit K0 fix (request R-36; lane k0fix). ONE TOKEN SPACE: A TOKEN IS BOTH A FAMILY AND A TARGET.
#
# Plant: memfn/src/targets.def's first family row is respelled with the first non-portable target's
# token (the pre-ruling spelling, where the family and its baseline target were both named alike).
# `-fmemfn-simd` takes a list that mixes family and target tokens (the owner's ruling 2026-11-07), so a
# token that names both has no reading. The family's default list names only targets, so no other
# structural rule sees the plant.
# Detector: memfn/tests/check_targets.sh (part 1 of tests/memfn/run_targets.sh, arm memfntargets): every
# family and target token must be distinct from every other; the entries' literal (part 2) is red too.
SAB_ID="S2981-targets-token-both-family-and-target"
SAB_FILE="memfn/src/targets.def"
SAB_SUITES="memfntargets"
SAB_DESC='a family token equals a target token: the table check must refuse a token with two readings'
SAB_DOC_FIGURE='MEASURED by lane k0fix, planted and reverted by hand in a scratch copy (k0fix_report.md, Distinctness check); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2981.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='MF_FAM_X86_64,  "x86_64",  "x86-64")'
SAB_AFTER='MF_FAM_X86_64,  "x86-64",  "x86-64")'
