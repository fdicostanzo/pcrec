#!/usr/bin/env bash
# S2981 -- [XARCH-DEV] unit K0 fix (request R-36; lane k0fix). ONE TOKEN SPACE: A FAMILY TOKEN IS ONE TYPO FROM A TARGET TOKEN.
#
# Plant: memfn/src/targets.def's first family row is respelled `x86_64`, the `uname -m` name the family
# had before the manager's change: it equals the target `x86-64` once `_` reads as `-`. `-fmemfn-simd` takes a
# list that mixes family and target tokens (the owner's ruling 2026-11-07); a one-character typo must not
# be another valid token. The family's default list names only targets and the parser is exact, so no other
# structural rule sees the plant.
# Detector: memfn/tests/check_targets.sh (part 1 of tests/memfn/run_targets.sh, arm memfntargets): no family
# token may equal a target token after folding `_` to `-`; the entries' literal (part 2) is red too.
SAB_ID="S2981-targets-token-both-family-and-target"
SAB_FILE="memfn/src/targets.def"
SAB_SUITES="memfntargets"
SAB_DESC='a family token equals a target token once _ reads as -: the table check must refuse it'
SAB_DOC_FIGURE='MEASURED by lane k0fix, planted and reverted by hand in a scratch copy (k0fix_report.md, Distinctness check); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2981.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='MF_FAM_X86_64,  "amd64", "x86-64",'
SAB_AFTER='MF_FAM_X86_64,  "x86_64", "x86-64",'
