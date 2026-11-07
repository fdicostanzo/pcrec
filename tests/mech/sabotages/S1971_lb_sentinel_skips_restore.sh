# S1971 ([VLOOKBEHIND] stage 1, design §7 W11 (b)) -- THE RESTORE ON LO_i'S SENTINEL PATH (UTF-8).
SAB_ID="S1971-lb-sentinel-skips-restore"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='the nearest start'\''s sentinel path jumps straight to the next branch, skipping L_n_i'\''s restore'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W11 (b) red under utf8 ((?<=é{2,3}|é)x on éx).'
SAB_COUNT=1
SAB_BEFORE='    const VmTgt k_none = range && !last ? pcrec_vm_tgt_label(L->n[i], false)'
SAB_AFTER='    const VmTgt k_none = range && !last ? pcrec_vm_tgt_label(bl[i + 1], false)   /* SABOTAGE S1971 */'
