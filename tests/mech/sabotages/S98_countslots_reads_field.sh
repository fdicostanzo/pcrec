# S98 — [M6.4.2] `vm_count_slots` READS `->possessive` INSTEAD OF `vm_cuts()`.
#
# R31 E4, as a row. `->possessive` is read at 23 sites over 8 functions, and
# THREE of them are PRE-PASSES that must agree with emission EXACTLY or the
# artifact is malformed rather than merely slow. `vm_count_slots` is the
# sharpest: it allocates the cut-mark slot, so a LIFT it cannot see runs
# `vm_slot_mark(v, v->nmark++)` past `RX_NSLOTS` — an OUT-OF-BOUNDS WRITE IN
# EMITTED CODE, K27's class, in a matcher a user compiles with their own
# `-fsanitize=undefined` and sees pcrec's name on.
#
# THIS DEFECT WAS FOUND LIVE DURING [M6.4.2], from the other end. RULE 3's
# condition-(d) decline was written into `vm_rep` alone, so the pre-pass took
# the REVDET arm while the emitter took the FRAMES arm: measured on
# `-fno-possessify '(?>(?:a|bc){2})d'`, the artifact emitted
# `RX_SET(RX_SLOT_REVDET0_ENTRY, resume_depth)` and `RX_CUT(2)` onto the revdet
# loop's OWN entry slot. That is why `vm_revdet_fits` is a predicate and why
# `[M6.4-ATOMIC rule 5c]` reads the slot map off the ARTIFACT.
SAB_ID="S98-countslots-reads-field"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness atomicdiff"
SAB_HARNESS_TARGET="tests/atomic_groups/possessive.rxt"
SAB_DESC="vm_count_slots's A_REP arm reads a->u.rep.possessive directly instead of the shared vm_cuts() predicate, so a LIFTED possessive's cut mark is never counted: the emitter then asks for a slot past RX_NSLOTS, or lands on another family's slot. An out-of-bounds write in EMITTED code (K27's class), or two live loops sharing one slot"
SAB_DOC_FIGURE="PREDICTED: codegen rule 5c RED (an RX_CUT naming a slot the legend does not declare a cut mark), slot-count assertions RED, and on a deep pattern an OOB slot write in the emitted matcher. Canonical figure owed from run_sabotage_matrix.sh S98."
SAB_COUNT=1
SAB_BEFORE='    case A_REP: {
        const bool cuts = vm_cuts(a, under_atomic);'
SAB_AFTER='    case A_REP: {
        const bool cuts = a->u.rep.possessive;   /* SABOTAGE S98 */
        (void)under_atomic;'
