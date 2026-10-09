#!/usr/bin/env bash
# S512 ([MEMFN] R4a, lane memfnmanifest) -- THE MANIFEST LOSES A ROW.
#
# The VMSTRIDE row is deleted. Its emitter, `vm_emit_span_scan`, is also
# named by the VMSPAN row, so rules 1 and 4 stay green on purpose: the only
# instrument that can be red is the K35 row-count floor, C17_ROW_FLOOR in
# tests/memfn/run_site_manifest.sh (a literal sharing no source with the
# TSV). SAB_REACH_POP asserts the row exists and the floor is still 14.
# RE-PINNED 2026-10-08 (lane m7fix): M7 (R-8, Q-R8-1) split N7U from N7, so
# the manifest holds 14 rows and C17_ROW_FLOOR is 14 (`=14` then a comment);
# the POP still read `=13$`, so the row scored UNREACHED. The form is lane
# m6's (e48cc296). The SETREST plant leaves 13 rows, below 14: same defect,
# same detector.
# RE-ANCHORED 2026-10-08 (D147 add. 12, lane m6): N6 retired, so the manifest
# holds 14 rows and C17_ROW_FLOOR is 14 (the POP had read 13 since the M7/M6
# floor raises; it now matches the live literal, `=14` then a comment). The
# SETREST plant leaves 13 rows, below 14: same defect, same detector.
# RE-ANCHORED 2026-10-08 ([MEMFN] R4h, lane r4h): VMSPAN went `delegated` and
# VMSTRIDE's emitter became `vm_stride_loop`, which no other row names, so
# deleting VMSTRIDE now ALSO trips rule 1 (an unlisted form). The row deleted
# is SETREST instead: its emitter `req_site_define` stays named by PRE and
# VERIFY, so, as before, only the K35 floor can be red (measured at the
# re-anchor: `FAIL: the manifest holds 12 rows, below its K35 floor of 13`,
# 17 passed / 1 failed). Same defect: one row gone, nothing else.
# RE-PINNED 2026-10-09 (lane vmlazy, R-12 REPLACE, Q-R12-2): VMLAZY deleted,
# so the manifest holds 13 rows and C17_ROW_FLOOR is 13; the SETREST plant
# leaves 12, below 13: same defect, same detector. Then R-12 (Q-R12-5) listed
# VALID: 14 rows, floor 14, the plant leaves 13.
SAB_ID="S512-c17-row-below-floor"
SAB_FILE="tests/memfn/site_manifest.tsv"
SAB_SUITES="memfnmanifest"
SAB_DESC='the SETREST row is deleted from the site manifest (its emitter stays listed by PRE and VERIFY), taking the row count below its K35 floor'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/memfnmanifest_report.md §4); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S512.'
SAB_REACH_POP='tests/memfn/site_manifest.tsv|^SETREST[[:space:]]+req_site_define[[:space:]]|1
tests/memfn/run_site_manifest.sh|^C17_ROW_FLOOR=14[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# The row's head is commented out, which deletes the row for every reader.
SAB_BEFORE=$'SETREST\treq_site_define\t'
SAB_AFTER=$'# SABOTAGE S512 (row deleted): SETREST\treq_site_define\t'
