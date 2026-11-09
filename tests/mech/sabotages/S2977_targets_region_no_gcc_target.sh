#!/usr/bin/env bash
# S2977 -- [XARCH-DEV] unit K0 (request R-36; lane k0), target_seam.md §6.1/§8. A REGION THAT DOES NOT
# APPLY UNDER GCC.
#
# Plant: memfn/src/targets.c's region text loses its gcc target pragma (the push/pop pair stays), so
# under gcc a part's functions compile at the consumer's own ISA.
# Detector: tests/memfn/targets_check.c (part 2 of tests/memfn/run_targets.sh, arm memfntargets): each
# target with a region has its region text held to push its needs for gcc and clang; the gcc target line is gone, so
# the check reads FAIL "target <canonical>: its region pushes its needs for gcc and clang, no arch=".
# Since the rule that a target whose fact checks failed is not compiled, the compile cells are skipped
# (counted), so the compile cells (part 3) no longer see this plant; the entry check is the catch.
SAB_ID="S2977-targets-region-no-gcc-target"
SAB_FILE="memfn/src/targets.c"
SAB_SUITES="memfntargets"
SAB_DESC='the region text drops its gcc target pragma: the region silently fails to apply under gcc'
SAB_DOC_FIGURE='MEASURED by lane s2977fix, planted by hand in a scratch copy: memfntargets 6 pass / 1 fail (the entries check), the compile cells skipped; exact re-run: bash tests/mech/run_sabotage_matrix.sh S2977.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    "#pragma GCC target(\"" attr "\")\n"                                       \'
SAB_AFTER='    "/* SABOTAGE S2977 */\n"                                                  \'
