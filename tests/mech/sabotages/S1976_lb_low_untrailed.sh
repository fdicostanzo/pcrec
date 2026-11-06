# S1976 ([VLOOKBEHIND] stage 1, design §7 W-low, FIXIND-5) -- LO_i IS TRAILED.
# A non-atomic lookahead moves the cursor backward, so a later evaluation can
# overwrite LO_i under a live candidate frame; only the trail rewinds it.
SAB_ID="S1976-lb-low-untrailed"
SAB_FILE="src/gen/vm_stmt.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='LO_i is written by an untrailed assignment (FIXIND-5: vm_set_line renders slot_values[SLOT_LB_LO*] = ... instead of RX_SET)'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): codegen RED on the W-low detector (residlbrange.c: 0 RX_SET lines, 1 raw write); harness W-low cell red ([2-2] lost: a budget give-up). asan confirmation and a --work-budget compile owed (report).'
SAB_COUNT=1
SAB_BEFORE='    if (name)
        pcrec_sb_printf(sb->b, "    %s_SET(%s_%s, %s);\n", sb->up, sb->up, name, src);'
SAB_AFTER='    if (name && !strncmp(name, "SLOT_LB_LO", 10))
        pcrec_sb_printf(sb->b, "    slot_values[%s_%s] = %s;\n", sb->up, name, src);   /* SABOTAGE S1976 */
    else if (name)
        pcrec_sb_printf(sb->b, "    %s_SET(%s_%s, %s);\n", sb->up, sb->up, name, src);'
