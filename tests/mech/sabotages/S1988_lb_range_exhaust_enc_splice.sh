# S1988 ([VLOOKBEHIND] stage 1, review r4 F17) -- AN ENCODING-KEYED SPLICE IN
# A NON-LAST VARYING BRANCH'S EXHAUSTION BLOCK (`L_n_i`, emit_vm.c's
# `vm_look_behind_retry`): a work-charge line emitted only where the backend
# carries a `decode` entry (utf8), i.e. encoding-owned text in the hot path,
# which DD-12 (7) forbids and DD12a(i) exists to see. Before F17 the only
# varying witness was one-branch positive, which has no `L_n_i`, and the
# default slice holds no lookbehind block: the splice was GREEN (review SEAM-3,
# plant PC). The `(?<=a{1,2}|b)x` / `(?<!a{1,2}|b)x` witnesses reach it.
SAB_ID="S1988-lb-range-exhaust-enc-splice"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="encoding"
SAB_DESC='a non-last varying lookbehind branch'\''s exhaustion block gains a utf8-only work-charge line (an encoding-keyed splice DD12a(i) must see)'
SAB_DOC_FIGURE='MEASURED (lane vlbfix, tools/review/plant.sh + run_encoding_checks.sh at the default 250-block slice; clean 14/0): 13 pass / 1 fail, DD12a(i) [K50] "2 pair(s) entered the gate-refinement class WITHOUT a manifest row" (first: (?<!a{1,2}|b)x). Red through the class'\''s no-unlisted-members guard rather than the strict bar: the splice moves RX_VM_PROGRAM_BYTES, a FORM stamp, so the pair reads as a declared form move (the review'\''s pre-existing VM_PROGRAM_BYTES note, unfixed here). Before F17'\''s two witnesses: GREEN.'
SAB_COUNT=1
SAB_BEFORE='    vm_lbl(v, L->n[i], "lookbehind: this branch is exhausted -- back to the cursor");
    pcrec_vm_b_seek(v->sb, VSK_RESTORE, posx, 0);'
SAB_AFTER='    vm_lbl(v, L->n[i], "lookbehind: this branch is exhausted -- back to the cursor");
    pcrec_vm_b_seek(v->sb, VSK_RESTORE, posx, 0);
    if (pcrec_enc_has_entry(pcrec_enc_by_id(v->cx->opt->encoding), PCREC_ENCE_DECODE))
        vm_work(v, "1", "SABOTAGE S1988");'
