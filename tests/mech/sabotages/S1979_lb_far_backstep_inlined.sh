# S1979 ([VLOOKBEHIND] stage 1, design §7 S133 twin, READY-1) -- THE FAR STEP IS
# THE SEAM'S. Inlining it changes no byte answer, so the fixture-declared
# per-site count is the detector.
SAB_ID="S1979-lb-far-backstep-inlined"
SAB_FILE="src/gen/vm_stmt.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='S133'\''s range twin: the far back-step (local count) renders scan_position - K inline instead of the seam call'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): codegen RED on the back_step per-site count (residlbrange: 3 -> 2); byte answers green; utf8 W6 cells red.'
SAB_COUNT=1
SAB_BEFORE='            pcrec_sb_printf(sb->b, "    scan_position = %s_back_step(subject, "
                                   "subject_length, scan_position, %s);\n",
                            sb->p, pcrec_vm_local_name(sb, s->u.seek.x));'
SAB_AFTER='            pcrec_sb_printf(sb->b, "    scan_position = scan_position >= %s ? scan_position - %s : (size_t)-1;\n",
                            pcrec_vm_local_name(sb, s->u.seek.x), pcrec_vm_local_name(sb, s->u.seek.x));   /* SABOTAGE S1979 */'
