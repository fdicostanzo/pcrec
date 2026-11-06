# S1964 ([VLOOKBEHIND] stage 1, design §7 S134 twin, READY-1) -- THE FAR
# STEP'S SENTINEL. Under UTF-8 the far count min(hi - lo, LO) is an upper bound
# and the far step can return the sentinel; the loop retries one shorter. A
# fall-through spelling underflows K and breaks every range cell, so the plant is
# the goto-L_try spelling, which only W6 sees.
SAB_ID="S1964-lb-far-sentinel-taken"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness encoding"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='S134'\''s range twin: the far back-step'\''s sentinel test always passes, so a sentinel position is tried as a candidate (the goto L_try spelling)'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W6 red under utf8 ((?<=(é{0,2}))x on éx); byte cells green (the far count is exact there).'
SAB_COUNT=1
SAB_BEFORE='    pcrec_vm_b_branch(v->sb, vm_condf(v, "scan_position != %s_BACK_STEP_NONE", v->p),
                      pcrec_vm_tgt_label(L->try_[i], false));'
SAB_AFTER='    pcrec_vm_b_branch(v->sb, vm_condf(v, "1 || scan_position != %s_BACK_STEP_NONE", v->p),
                      pcrec_vm_tgt_label(L->try_[i], false));   /* SABOTAGE S1964 */'
