#!/usr/bin/env bash
# S684 ([MEMFN] M6, lane m6) -- THE VM RE-SPELLS ITS STRIDED LOOP (S673's
# analogue). VMSTRIDE is delegated: vm_emit_span_scan names the site and the
# kit writes the loop. The plant has pcrec spell an open strided `while ((`
# itself at stride > 1: C17 rule 3 (a delegated emitter spells a form) and
# C12 (a walk-open form in emit_vm.c with no ceiling row) both fire.
SAB_ID="S684-m6-vm-respells-strided-loop"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="memfnmanifest memfnforms"
SAB_DESC='pcrec'"'"'s VM span scan spells its own strided while loop again at stride > 1 instead of the kit'"'"'s VMSTRIDE site, while VMSTRIDE is delegated: two spellings of one search (D122)'
SAB_DOC_FIGURE="HAND-MEASURED by lane m6 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m6_report.md section 6): F684. The matrix figure is owed at the slot."
SAB_REACH='"$PCREC" -p rx --engine=vm -o - --pattern "(?:ab)+c"'
SAB_REACH_EXPECT='while ((rx_span_cursor + 2 <= subject_length) && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98)) {'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    DelegSite id = stride == 1 ? DELEG_VMSPAN : DELEG_VMSTRIDE;
    mf_hooks h;
    mf_site *s = pcrec_memfn_advance_site(v->cx, id, &sa, &h);
    pcrec_memfn_emit(v->cx, id, s, &h, b);'
SAB_AFTER='    DelegSite id = stride == 1 ? DELEG_VMSPAN : DELEG_VMSTRIDE;
    mf_hooks h;
    mf_site *s = pcrec_memfn_advance_site(v->cx, id, &sa, &h);
    if (stride > 1)  /* SABOTAGE S684: pcrec spells the strided loop again */
        pcrec_sb_printf(b, "        while ((%s_span_cursor + %d <= %s)) {\n"
                           "            %s_span_cursor += %d;\n        }\n",
                        v->p, stride, bound, v->p, stride);
    else
    pcrec_memfn_emit(v->cx, id, s, &h, b);'
