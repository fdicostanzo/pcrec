# S1970 ([VLOOKBEHIND] stage 1, design §7 W11 (a)) -- L_n_i RESTORES THE CURSOR.
SAB_ID="S1970-lb-exhaustion-no-restore"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='an exhausted varying branch goes to the next branch without restoring the cursor from POS'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W11 (a) red ((?<=a{1,2}|b)x on bx, (?<=a{1,2}|bc)x on bcx); the a{2,3} control stays green (its guard skips the branch).'
SAB_COUNT=1
SAB_BEFORE='    pcrec_vm_b_seek(v->sb, VSK_RESTORE, posx, 0);'
SAB_AFTER='    /* SABOTAGE S1970: the exhaustion restore dropped */'
