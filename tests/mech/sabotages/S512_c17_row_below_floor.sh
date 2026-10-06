#!/usr/bin/env bash
# S512 ([MEMFN] R4a, lane memfnmanifest) -- THE MANIFEST LOSES A ROW.
#
# The VMSTRIDE row is deleted. Its emitter, `vm_emit_span_scan`, is also
# named by the VMSPAN row, so rules 1 and 4 stay green on purpose: the only
# instrument that can be red is the K35 row-count floor, C17_ROW_FLOOR in
# tests/memfn/run_site_manifest.sh (a literal sharing no source with the
# TSV). SAB_REACH_POP asserts the row exists and the floor is still 13.
SAB_ID="S512-c17-row-below-floor"
SAB_FILE="tests/memfn/site_manifest.tsv"
SAB_SUITES="memfnmanifest"
SAB_DESC='the VMSTRIDE row is deleted from the site manifest (its emitter stays listed by VMSPAN), taking the row count below its K35 floor'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/memfnmanifest_report.md §4); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S512.'
SAB_REACH_POP='tests/memfn/site_manifest.tsv|^VMSTRIDE[[:space:]]+vm_emit_span_scan[[:space:]]|1
tests/memfn/run_site_manifest.sh|^C17_ROW_FLOOR=13$|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# The row's head is commented out, which deletes the row for every reader.
SAB_BEFORE=$'VMSTRIDE\tvm_emit_span_scan\t'
SAB_AFTER=$'# SABOTAGE S512 (row deleted): VMSTRIDE\tvm_emit_span_scan\t'
