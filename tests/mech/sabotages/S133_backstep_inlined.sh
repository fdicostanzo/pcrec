# S133 ([M6.6.2] wave D, design row S-LA6) — THE BACK-STEP IS INLINED INSTEAD
# OF ROUTED THROUGH THE SEAM.
#
# S109's SHAPE ONE CONSTRUCT OVER, AND IT CHANGES NO ANSWER. Under the byte
# backend one byte is one character, so `scan_position - k` is EXACTLY what
# `<prefix>_back_step` computes; every corpus cell, every differential and
# every oracle in this tree stays green while the artifact has acquired
# encoding-sensitive byte arithmetic in SHARED EMITTER CODE. That is the
# residue class D58 scope item 3 enumerates by name, and the [M6.6] plan row
# forbids it in its own text: "a seam entry, never raw `pos - k` byte
# arithmetic in shared emitter code".
#
# A UTF-8 BACKEND WOULD THEN BE UNFIXABLE FROM src/gen/enc/. `k` is a count of
# CHARACTERS; under UTF-8 the position `k` characters back is a walk over
# continuation bytes that can also fail on a malformed sequence — which is why
# the entry takes `s` and `n` at all, and why it returns a SENTINEL. An emitter
# that subtracts cannot be corrected by adding a backend.
#
# IT IS A TWO-SITE ROW BY NECESSITY (tests/mech/CLAUDE.md's S108 mechanism).
# The emission and the enc-mask OR must move TOGETHER: leaving the mask alone
# would make the artifact declare an entry it never calls, and the [M5-SEAM]
# check would then fire for the WRONG REASON (the declared-entry-set half
# rather than the call-count half) — a row that goes red for a reason it did
# not name is not a detector. Dropping the mask also removes the
# `<prefix>_BACK_STEP_NONE` macro, so site 1 must delete the sentinel
# comparison with the call or the artifact does not compile.
#
# WHAT CATCHES IT is the codegen check's fixture-DECLARED per-site count: the
# artifact must call `rx_back_step` exactly as many times as the fixture says
# (one per top-level branch), and an inlined back-step calls it zero times.
# Nothing behavioural can.
SAB_ID="S133-backstep-inlined"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind.rxt"
SAB_DESC="vm_look_behind emits 'scan_position - k' inline instead of calling the encoding residual back-step, and drops the PCREC_ENCE_BACK_STEP mask bit with it. Under the byte backend the ANSWERS ARE IDENTICAL, so every corpus and every differential stays green; what moves is that the back-step stopped being replaceable by another encoding's backend"
SAB_DOC_FIGURE="PREDICTED: codegen RED on the per-site count for the residlb1/residlb2/residlb3/residlbneg/residlbna/residlbtwo/residlbbref fixtures AND on the declared-entry-set half; tests/lookaround and the lookaround differential GREEN. Canonical figure owed from run_sabotage_matrix.sh S133."
SAB_COUNT=1
SAB_BEFORE='        sb_printf(b, "    scan_position = %s_back_step(subject, "
                     "subject_length, scan_position, %d);\n", v->p, k);
        vm_ev(v, VE_NOTE, 0, 0, vm_rolef(v,
              "lookbehind: the ENCODING SEAM'"'"'s back-step, %d character%s",
              k, k == 1 ? "" : "s"));
        sb_printf(b, "    if (scan_position == %s_BACK_STEP_NONE) goto %s_fail;\n",
                  v->p, v->p);'
SAB_AFTER='        sb_printf(b, "    scan_position = scan_position - %d;"
                     "   /* SABOTAGE S133: inlined, not routed */\n", k);
        vm_ev(v, VE_NOTE, 0, 0, "SABOTAGE S133: inlined back-step");'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='    v->enc_mask |= PCREC_ENCE_BACK_STEP;'
SAB_AFTER2='    /* SABOTAGE S133: the mask OR dropped with the call */'
