#!/usr/bin/env bash
# S511 ([MEMFN] R4a, lane memfnmanifest) -- A STALE PENDING ROW.
#
# A site whose search the kit renders is listed `pending` while its emitter
# spells no search form (the shape a REPLACE commit has when it moves the
# search into the kit and forgets to flip the row). Detector: C17 rule 4.
# RE-AIMED 2026-10-06 ([MEMFN] R4c REPLACE, lane r4ccore): the plant was the
# PRE row's one-byte pre-check (`emit_req_one_byte`) until PRE went
# `delegated` at R4c; it moved to MLINE, a still-pending one-form emitter.
# RE-AIMED 2026-10-08 ([MEMFN] M4 REPLACE, lane m4; ruling R1): MLINE went
# `delegated`, so the plant moved to VMSTRIDE's `vm_stride_loop`.
# RE-AIMED 2026-10-08 ([MEMFN] M6 REPLACE, lane m6; RULED Q-R10-8): M6 deleted
# `vm_stride_loop` (its anchor) and flipped VMSTRIDE to `delegated`, and the
# pending rows left (N6, N7U, VMLAZY) are each one migration from leaving too.
# NOTE 2026-10-08 (D147 add. 12, lane m6): N6 was RETIRED (not a search site);
# the pending rows are now N7U and VMLAZY. The plant (VMSTRIDE) is unaffected.
# NOTE 2026-10-09 (R-12 REPLACE, lane vmlazy): VMLAZY deleted; the pending
# row is N7U alone. The plant (VMSTRIDE) is unaffected.
# NOTE 2026-10-09 (lane n7uret, D147 add. 14): N7U retired; VALID is the
# pending row. The plant (VMSTRIDE) is unaffected.
# So the plant moves to the MANIFEST: the delegated VMSTRIDE row is flipped
# back to `pending`. Its emitters (vm_span_advance, vm_emit_span_scan) spell
# no form, the kit renders the loop, so rule 4 fires. Intent unchanged: a
# pending row whose emitter spells nothing. Durable: it needs only one
# delegated row whose emitters spell no form, which every REPLACE makes.
# SAB_REACH_POP asserts the VMSTRIDE row is `delegated` and names
# `vm_span_advance`.
SAB_ID="S511-c17-stale-pending-row"
SAB_FILE='tests/memfn/site_manifest.tsv'
SAB_SUITES="memfnmanifest"
SAB_DOC_FIGURE='RE-MEASURED 2026-10-08 after D147 add. 12 (N6 retired; lane m6): 2 failed / 12 passed. HAND-MEASURED by lane m6 2026-10-08 at the re-aim (plant applied; docs/dev/lanes/m6_report.md section 6): memfnmanifest 2 failed / 13 passed (rule 4 on vm_span_advance and vm_emit_span_scan, pending VMSTRIDE). Earlier figures: docs/dev/lanes/memfnmanifest_report.md section 4, m4_report.md section 6. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S511.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH_POP='tests/memfn/site_manifest.tsv|^VMSTRIDE[[:space:]]+vm_span_advance,vm_emit_span_scan[[:space:]].*[[:space:]]delegated[[:space:]]|1'
SAB_DESC='the VMSTRIDE manifest row is flipped back to pending while its emitters (vm_span_advance, vm_emit_span_scan) spell no search form, the kit rendering the loop: a stale pending row'
SAB_BEFORE='	M6	delegated	vm_cursor_rep,vm_cls_test	'
SAB_AFTER='	M6	pending	vm_cursor_rep,vm_cls_test	'
