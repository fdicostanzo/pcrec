# S1977 ([VLOOKBEHIND] stage 1, design §7 fwd_step (i)) -- THE STEP IS THE SEAM'S.
SAB_ID="S1977-fwd-step-inlined"
SAB_FILE="src/gen/vm_stmt.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='$_fwd_step inlined: the VSK_STEP_CHAR arm renders scan_position += 1 (S133'\''s shape for the forward entry)'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): codegen RED on [M5-SEAM]'\''s fwd_step per-site count (residlbrange, residlbrangeu8); byte answers green; utf8 W6/W14 cells red.'
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(sb->b, "    scan_position = %s_fwd_step(subject, "
                               "(size_t)slot_values[%s], scan_position);\n",
                        sb->p, s->u.seek.slotx);'
SAB_AFTER='        pcrec_sb_printf(sb->b, "    scan_position += 1;\n");   /* SABOTAGE S1977 */'
