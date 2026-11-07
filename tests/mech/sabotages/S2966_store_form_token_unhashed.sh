#!/usr/bin/env bash
# S2966 -- span_pick stage 2 unit S2e, sabotage (u) (docs/design/memfn/span_cards.md §2.4, §9's S2e row;
# lane memfn-s2e). A COMMITTED FORMAT-2 SET'S FORM TOKEN RENAMED TO AN ID WITH NO HASH.
#
# Plant: zen4-grid3@1's row kit.find_byte.libc renamed kit.find_byte.libcx (the key's form token libcx is no
# form id of the R-MS3 entry table).
# Detector: tests/memfn/finder_check.py check C's measure_store pass (arm memfnfinder): in a format-2 set a
# form token must resolve through arm_fixtures --hash, red, never "later". (The edit also moves the set's
# digest and file sha, which test-knowledge sees; this row's suite is memfnfinder alone.)
SAB_ID="S2966-store-form-token-unhashed"
SAB_FILE="measure_store/zen4-grid3/1/set.tsv"
SAB_SUITES="memfnfinder"
SAB_DESC='a committed format-2 set row whose form token names no form id (resolves to no hash)'
SAB_DOC_FIGURE='MEASURED by lane memfn-s2e planted and reverted by hand (report, Sabotage); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2966.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='kit.find_byte.libc	ratio	'
SAB_AFTER='kit.find_byte.libcx	ratio	'
