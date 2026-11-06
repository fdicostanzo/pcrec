# S1961 ([VLOOKBEHIND] stage 1, design §7 W2) -- THE END-CHECK ON A VARYING
# BRANCH. Each candidate's body must end exactly at the cursor; without the
# check a body ending earlier is a match.
SAB_ID="S1961-lb-range-endcheck-removed"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='a varying branch'\''s end-check never fires, so a candidate whose body ends before the cursor is accepted'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W2 red ((?<=a{1,2})x on abx: a false match (2,3)); W3 red. One-length cells green (their end-check is unchanged).'
SAB_COUNT=1
SAB_BEFORE='            pcrec_vm_b_branch(v->sb, vm_condf(v, "scan_position != (size_t)slot_values[%s]", sl),
                        pcrec_vm_tgt_fail());'
SAB_AFTER='            pcrec_vm_b_branch(v->sb, vm_condf(v, range ? "0 && scan_position != (size_t)slot_values[%s]" : "scan_position != (size_t)slot_values[%s]", sl),
                        pcrec_vm_tgt_fail());   /* SABOTAGE S1961 */'
