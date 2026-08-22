# S116 (design row S-BR13) — THE REVDET CAPTURE SUPPRESSION DROPS THE PENDING
# SLOT BUT KEEPS THE PAIR.
#
# R32 E9's UNNAMED INTERACTION, made a row. The reverse-deterministic rung
# SUPPRESSES a body's per-iteration capture writes (`v->nocap`) — that
# per-iteration trail growth is the whole cost the rung exists to remove — and
# §3.4's backward walk reconstructs the last iteration's values afterwards.
# The shape that makes it interesting is a group INSIDE the loop with the
# reference OUTSIDE it (`(?:(a|bb)x)+\1`), where the reference reads slots the
# BACKWARD WALK wrote rather than slots the loop wrote.
#
# WHY THE PENDING WRITE AND THE PAIR ARE ONE PUBLICATION. Publish-at-close
# splits `A_CAP`'s emission into a pending write at the open and two published
# writes at the close. Suppressing HALF of it leaves the backward walk's
# reconstructed pair sitting beside a stale pending value from an earlier
# iteration — and on the next traverse that stale value is published as a
# capture. The design's answer is to write the suppression as ONE guarded
# block so "in step with the pair" is structural rather than a rule someone
# has to remember; this row is what happens when it is not.
#
# The interaction was traced CORRECT and UNTESTED in the first design. It is
# `nested.rxt`'s group-in-body block that sees it.
SAB_ID="S116-revdet-drops-pending"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="brefdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/nested.rxt"
SAB_DESC="A_CAP's PENDING write is emitted unconditionally while the published pair stays under the revdet suppression, so inside a reverse-deterministic loop's forward scan the two halves of one publication come apart. The reference then reads a pair published from a stale pending value"
SAB_DOC_FIGURE="PREDICTED: brefdiff RED; the corpus RED on nested.rxt's group-in-body block ((?:(a|bb)x)+\\1). Canonical figure owed from run_sabotage_matrix.sh S116."
SAB_COUNT=1
SAB_BEFORE='        if (!v->nocap) {
            if (marked)
                vm_set(v, vm_slot_pend(v, a->capno), "(ptrdiff_t)scan_position",'
SAB_AFTER='        if (1) {   /* SABOTAGE S116: the pending write escapes the suppression */
            if (marked)
                vm_set(v, vm_slot_pend(v, a->capno), "(ptrdiff_t)scan_position",'
