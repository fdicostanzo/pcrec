#!/usr/bin/env bash
# S511 ([MEMFN] R4a, lane memfnmanifest) -- A STALE PENDING ROW.
#
# A pending row's emitter is respelled so its one search form becomes a call
# the vocabulary does not know (the shape a REPLACE commit has when it moves
# the search into the kit and forgets to flip the row): the row stays
# `pending` while its emitter spells nothing. Detector: C17 rule 4.
# SAB_REACH_POP asserts the VMSTRIDE row is `pending` and names
# `vm_stride_loop`.
# RE-AIMED 2026-10-06 ([MEMFN] R4c REPLACE, lane r4ccore): the plant was the
# PRE row's one-byte pre-check (`emit_req_one_byte`) until PRE went
# `delegated` at R4c; it moved to MLINE, a still-pending one-form emitter.
# RE-AIMED 2026-10-08 ([MEMFN] M4 REPLACE, lane m4; ruling R1): MLINE went
# `delegated` (emit_attempt's `memchr(` is the kit's), so the plant moves to
# VMSTRIDE, still pending until M6: `vm_stride_loop` (src/gen/emit_vm.c) spells
# one form, the open strided `while ((` (vocabulary walk-open), which the
# plant respells as a kit-style call. Intent unchanged: the emitter stops
# spelling its one form while its row stays pending (rule 4). The plant also
# lowers C12's emit_vm.c walk-open group below its ceiling; that is arm
# memfnforms', not this row's.
SAB_ID="S511-c17-stale-pending-row"
SAB_FILE='src/gen/emit_vm.c'
SAB_SUITES="memfnmanifest"
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/memfnmanifest_report.md §4; re-aimed docs/dev/lanes/m4_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S511.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH_POP='tests/memfn/site_manifest.tsv|^VMSTRIDE[[:space:]]+vm_stride_loop[[:space:]].*[[:space:]]pending[[:space:]]|1'
SAB_DESC='vm_stride_loop stops spelling its open strided while (( (respelled as a kit-style call) while the VMSTRIDE manifest row stays pending: a stale row'
SAB_BEFORE='    pcrec_sb_printf(b, "        while ((%s_span_cursor + %d <= %s)", v->p, stride, bound);'
SAB_AFTER='    pcrec_sb_printf(b, "        pcrec_mf_stride((%s_span_cursor + %d <= %s)", v->p, stride, bound);  /* SABOTAGE S511 */'
