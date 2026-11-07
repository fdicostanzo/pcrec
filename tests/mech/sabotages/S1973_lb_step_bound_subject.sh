# S1973 ([VLOOKBEHIND] stage 1, design §7 W13) -- THE STEP IS BOUNDED BY THE CURSOR.
SAB_ID="S1973-lb-step-bound-subject"
SAB_FILE="src/gen/vm_stmt.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='the one-character step is bounded by the subject length instead of the cursor in POS'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W13 red under utf8 (a stray continuation byte at the cursor: the step jumps past it and runs until a budget gives up).'
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(sb->b, "    scan_position = %s_fwd_step(subject, "
                               "(size_t)slot_values[%s], scan_position);\n",
                        sb->p, s->u.seek.slotx);'
SAB_AFTER='        pcrec_sb_printf(sb->b, "    scan_position = %s_fwd_step(subject, "
                               "subject_length, scan_position);\n",
                        sb->p);   /* SABOTAGE S1973 */'
