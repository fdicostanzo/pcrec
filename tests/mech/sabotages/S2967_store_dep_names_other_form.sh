#!/usr/bin/env bash
# S2967 -- span_pick stage 2 unit S2e, sabotage (u2) (docs/design/memfn/span_cards.md §2.4 READY-8, §9's S2e
# row; lane memfn-s2e). A ROW'S RECORDED DEP NAMES ANOTHER FORM'S ID.
#
# Plant: zen4-grid3@1's kit.find_byte.libc row records kit:form.walk=<libc's hash> instead of kit:form.libc=...
# (deps are provenance: the digest and the loader never read them).
# Detector: tests/memfn/finder_check.py check C's measure_store pass (arm memfnfinder): the recorded id must be
# the row's form token. (The file sha moves too, which test-knowledge sees; this row's suite is memfnfinder.)
SAB_ID="S2967-store-dep-names-other-form"
SAB_FILE="measure_store/zen4-grid3/1/set.tsv"
SAB_SUITES="memfnfinder"
SAB_DESC='a committed format-2 set row whose recorded kit:form dep names another form id'
SAB_DOC_FIGURE='MEASURED by lane memfn-s2e planted and reverted by hand (report, Sabotage); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2967.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='	-	-	kit:form.libc=d7672e87c1dd6d97	-	slot J2'
SAB_AFTER='	-	-	kit:form.walk=d7672e87c1dd6d97	-	slot J2'
