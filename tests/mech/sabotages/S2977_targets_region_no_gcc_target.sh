#!/usr/bin/env bash
# S2977 -- [XARCH-DEV] unit K0 (request R-36; lane k0), target_seam.md §6.1/§8. A REGION THAT DOES NOT
# APPLY UNDER GCC.
#
# Plant: memfn/src/targets.c's region text loses its gcc target pragma (the push/pop pair stays), so
# under gcc a part's functions compile at the consumer's own ISA.
# Detector: tests/memfn/run_targets.sh (arm memfntargets): the compile cells (part 3; the 32-byte
# fixture part no longer compiles at gcc's default -march) and the entries' region text (part 2).
SAB_ID="S2977-targets-region-no-gcc-target"
SAB_FILE="memfn/src/targets.c"
SAB_SUITES="memfntargets"
SAB_DESC='the region text drops its gcc target pragma: the region silently fails to apply under gcc'
SAB_DOC_FIGURE='MEASURED by lane k0, planted and reverted by hand in a scratch copy (k0_report.md, Sabotage); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2977.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    "#pragma GCC target(\"" attr "\")\n"                                       \'
SAB_AFTER='    "/* SABOTAGE S2977 */\n"                                                  \'
