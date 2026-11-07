#!/usr/bin/env bash
# S2978 -- [XARCH-DEV] unit K0 (request R-36; lane k0). THE FAMILY GUARD ADMITS AN ILP32 ABI.
#
# Plant: memfn/src/targets.def's first family guard loses its ILP32 exclusion, so the x32 ABI (which
# also defines the family's architecture macro) passes the guard; the kit's own host chain keeps it.
# Detector: memfn/tests/check_targets.sh (part 1 of tests/memfn/run_targets.sh, arm memfntargets): the
# host cell gcc-mx32 reads the guard holding where the host chain names no family.
SAB_ID="S2978-targets-guard-admits-ilp32"
SAB_FILE="memfn/src/targets.def"
SAB_SUITES="memfntargets"
SAB_DESC='a family guard loses its ILP32 exclusion: the guard and the host chain disagree on x32'
SAB_DOC_FIGURE='MEASURED by lane k0, planted and reverted by hand in a scratch copy (k0_report.md, Sabotage); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2978.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"defined(__x86_64__) && !defined(__ILP32__)", "x86-64")'
SAB_AFTER='"defined(__x86_64__)", "x86-64")'
