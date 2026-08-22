# S97 — [M6.4.2] THE DISCHARGE'S OUTPUT INHERITS THE DISCHARGED NODE'S STAMP.
#
# D67 CONTRACT NOTE 3, as a row, and it is the subtlest of the thirteen: *"a
# discharge's output must not inherit the discharged node's stamp, or the
# fixpoint never converges to DFA with every answer still correct."*
#
# THE FAILURE SHAPE IS "CHANGES NO ANSWER", which is what makes it a row rather
# than a corpus case. The free discharge deletes an `A_ATOMIC` whose cut §2.2
# proves dead and splices its `A_REP` body back in. If the spliced body
# inherited the group's VM_ONLY stamp, the tree would still be correct — every
# match, every capture, every refusal identical — and the pattern would simply
# never become DFA-compilable. `[^"]*+"` would keep compiling to the VM
# forever, and the per-PATTERN split Frank's 2026-08-12 note asks for would
# quietly stop existing while every test in the tree stayed green.
#
# THE ONLY THING THAT SEES IT is `tests/registry/registry_check.c`'s
# `check_free_discharge`, which asserts the OTHER direction of the split: a
# provably-dead cut must compile to a PURE DFA under `--engine=dfa`. That check
# exists for this row.
SAB_ID="S97-discharge-inherits-stamp"
SAB_FILE="src/opt/atomic.c"
SAB_SUITES="registry codegen harness atomicdiff"
SAB_HARNESS_TARGET="tests/atomic_groups/possessive.rxt"
SAB_DESC="the free discharge copies the discharged A_ATOMIC's registry stamp onto the A_REP it splices in, so SR-8's consultation still sees a DFA-excluding node and the pattern stays VM-forced. EVERY ANSWER IS UNCHANGED -- only the ENGINE moves -- which is exactly the 'changes no answer' shape D67 note 3 warns about and which no corpus case can see"
SAB_DOC_FIGURE="PREDICTED: registry's check_free_discharge RED ('a*+b' refuses under --engine=dfa instead of compiling to a pure DFA), codegen rule 4 RED (the discharged artifact still carries RX_ENGINE), and the WHOLE CORPUS GREEN. Canonical figure owed from run_sabotage_matrix.sh S97."
SAB_COUNT=1
SAB_BEFORE='        if (ds_has(d, a) && a->l->k == A_REP) return a->l;'
SAB_AFTER='        if (ds_has(d, a) && a->l->k == A_REP) {
            a->l->reg = a->reg;   /* SABOTAGE S97: the output inherits the stamp */
            return a->l;
        }'
