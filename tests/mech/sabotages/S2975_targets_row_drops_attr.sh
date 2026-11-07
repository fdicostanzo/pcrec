#!/usr/bin/env bash
# S2975 -- [XARCH-DEV] unit K0 (request R-36; lane k0), the table check's COMPILER CONTROL
# (docs/design/memfn/target_seam_units.md §5, R2). THE 32-BYTE TARGET LOSES ONE ATTRIBUTE.
#
# Plant: memfn/src/targets.def's 32-byte target row drops R2's attribute from both its region attributes and its
# features (the row as target_seam.md §2 first wrote it), so the columns still agree with each other.
# Detector: memfn/tests/check_targets.sh (part 1 of tests/memfn/run_targets.sh, arm memfntargets): gcc
# at the family floor plus the row's attributes no longer defines what gcc's own -march for that row
# defines (one macro short); the entries' literal features row (part 2) is red too.
SAB_ID="S2975-targets-row-drops-attr"
SAB_FILE="memfn/src/targets.def"
SAB_SUITES="memfntargets"
SAB_DESC='the 32-byte target row loses one attribute from both columns: the compiler control must see it'
SAB_DOC_FIGURE='MEASURED by lane k0, planted and reverted by hand in a scratch copy (k0_report.md, Sabotage); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2975.'
SAB_EXPECT=DETECTED
SAB_COUNT=2
SAB_BEFORE='popcnt,sahf,sse4.1'
SAB_AFTER='popcnt,sse4.1'
