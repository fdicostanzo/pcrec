# S216 ([OPT-4.2]) — THE RUNGLESS NULLABILITY DECLINE NEUTERED.
#
# WHAT IT BREAKS. [OPT-4.1] declines a ladder RUNG's count-collapsed rescue
# when the collapsed language is nullable (a filter admitting a zero-length
# match at every position can dismiss none of them). [OPT-4.2] generalizes
# the SAME predicate to the ORDINARY hybrid path, where NO rung ever ran and
# the pattern's own EXACT language is nullable: `src/opt/select_engine.c`'s
# fit site computes `fit.prefilter_declined_nullable_default` off the shared
# `lang_nullable_declinable` local, guarded by `collapse_reason == CR_NONE`,
# `!cx->dfa_disabled` and `would_prefilter`. This sabotage forces the field
# to `false` unconditionally, which reproduces [OPT-4.2]'s ENTIRE pre-fix
# state: an ordinary VM-chosen pattern whose own language is nullable
# (captures forcing the VM, no backreference, no linked call, no
# `-fprefilter`/`-fno-prefilter`) goes back to building and shipping its
# exact prefilter unconditionally — a scan that can never dismiss a
# position (pcrec-bench O-10 measured the analogous collapsed shape at
# 1.2-9.9x slower than none).
#
# WHY NO .rxt CORPUS AND NO DIFFERENTIAL CAN SEE THIS. The decline is
# ANSWER-IDENTITY-PRESERVING BY DESIGN (docs/spec/tuning.md SS2.17's own
# rule, carried over unchanged from [OPT-4.1]): the hybrid's DFA-erasure
# window is a FILTER, and the VM re-derives the true answer from every
# candidate it is handed regardless of whether the filter is present at
# all (S6.1/S4.7's exactness claim; tests/vm/run_vm_tests.sh SS3.7's own
# differential covers that half). So every .rxt corpus, the vm oracle
# sweep, and the S3.7 differential all still agree with this sabotage
# applied — the artifact SHIPS A DIFFERENT MECHANISM and answers every
# subject identically, which is exactly the shape D46 exists to make
# OBSERVABLE through a stamp rather than leaving it to be found by luck.
#
# WHAT ACTUALLY HAPPENS, measured by hand against the design (the mech
# matrix itself is the manager's battery, not this lane's — this row is
# filed with its predicted detection, per S213's own precedent of
# recording the argument before the battery run): `'(a)*'` (captures force
# the VM; the pattern's own language matches the empty string) goes back to
# stamping `RX_VM_PREFILTER "hybrid"` and `RX_ENGINE_SEL "selected"`
# instead of `"none"`/`"declined-nullable-default"`, and the `--emit-ir`
# listing's `; prefilter` line reads "yes -- the capture-erased ..." instead
# of naming the nullable language. tests/prefilter/run_prefilter_tests.sh's
# `[OPT-4.2]` section (checks 1 and 4) is what reads the artifact this way;
# no other suite in the tree does.
SAB_ID="S216-opt42-default-decline-neutered"
SAB_FILE="src/opt/select_engine.c"
SAB_SUITES="prefilter"
SAB_DESC="fit.prefilter_declined_nullable_default (the [OPT-4.2] rungless nullability decline) is forced to false unconditionally, so an ordinary VM-chosen nullable pattern ('(a)*': captures force the VM, own language matches empty) goes back to building and shipping its exact prefilter unconditionally -- RX_VM_PREFILTER reverts to 'hybrid' and RX_ENGINE_SEL to 'selected' instead of 'none'/'declined-nullable-default'. Answer-identity-preserving by design (the VM re-derives the true answer regardless of the filter), so no .rxt corpus, no differential and no other structural check can see it -- only tests/prefilter/run_prefilter_tests.sh's [OPT-4.2] section (checks 1 and 4) reads the stamp/listing this way"
SAB_DOC_FIGURE="docs/spec/tuning.md SS2.17's [OPT-4.2] subsection; src/opt/CLAUDE.md's [OPT-4.2] section; docs/spec/match_api.md SS6.3's declined-nullable-default value-table row. HAND-TRACED by lane o42 (2026-08-31) against the box hold; the mech matrix's own DETECTED figure is owed at the manager's battery run once the hold lifts"
SAB_COUNT=1
SAB_BEFORE='        fit.prefilter_declined_nullable_default =
            cx->collapse_reason == CR_NONE && !cx->dfa_disabled &&
            lang_nullable_declinable && would_prefilter;'
SAB_AFTER='        /* SABOTAGE S216: the rungless decline never fires. */
        fit.prefilter_declined_nullable_default = false;'
