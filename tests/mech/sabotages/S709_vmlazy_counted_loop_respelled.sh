#!/usr/bin/env bash
# S709 ([MEMFN] R-12, lane vmlazy) -- PCREC RE-SPELLS THE COUNTED LOOP.
# The lazy rmin prefix is the kit's VMSPAN/VMSTRIDE site and the VMLAZY row is
# deleted. The plant puts M6's counted loop back (`while (it_ < %dUL) {`) in
# front of the scan: the `span-count` vocabulary line, KEPT at C12 ceiling 0
# by RULING Q-R12-6, sees it (memfnforms), and no pending row names
# vm_cursor_rep, so C17 rule 1 fires (memfnmanifest).
SAB_ID="S709-vmlazy-counted-loop-respelled"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="memfnforms memfnmanifest"
SAB_DESC='pcrec'"'"'s VM cursor rung spells its old counted rmin loop again beside the kit'"'"'s VMSPAN/VMSTRIDE site: two spellings of one search (D122)'
SAB_DOC_FIGURE="HAND-MEASURED by lane vmlazy 2026-10-09 (one mech row, solo): see docs/dev/lanes/vmlazy_report.md §5. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S709."
SAB_REACH_POP='tests/memfn/search_vocab.tsv|^span-compare[[:space:]]+span-count[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            vm_emit_span_scan(v, seq, stride, members, NULL, a->u.rep.rmin);'
SAB_AFTER='            pcrec_sb_printf(b, "    {\n        unsigned long it_ = 0;\n        while (it_ < %dUL) {\n        }\n    }\n", a->u.rep.rmin);  /* SABOTAGE S709 */
            vm_emit_span_scan(v, seq, stride, members, NULL, a->u.rep.rmin);'
