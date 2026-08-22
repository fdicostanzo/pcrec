# S95 — [M6.4.2] `vm_cost`'s A_ATOMIC ARM CHARGES NO TRAIL ENTRY.
#
# R31 C10, and the design's own bullet said "no new give-up code; the caps are
# unchanged" before the panel refuted it. The atomic group's mark is written
# with `vm_set`, which is the TRAILED writer — that is what makes NESTING and
# RE-ENTRY work, since an outer backtrack restores the mark and the entry label
# re-sets it — so an `A_ATOMIC` inside a quantifier costs ONE TRAIL ENTRY PER
# ENTRY TO THE GROUP, multiplied by the enclosing repeat exactly as A_CAP's two
# writes are.
#
# THE `\K` ANALOGUE ONE CONSTRUCT OVER. `tests/mech/sabotages/
# S87_kreset_trail_uncharged.sh` is the same defect for `\K` and its own header
# explains why such a row needs to exist separately: an under-sized bound is
# not a wrong ANSWER, it is a REFUSAL to answer (`PCREC_ERR_FRAMES` on a
# pattern the artifact can match), and refusals are exactly what a corpus of
# matching cells is worst at noticing unless somebody wrote cells that reach
# the bound.
#
# NOTHING IS EMITTED DIFFERENTLY under this row — the artifact simply declares
# an array too small for the program beside it — so every structural check
# stays green and only a deep-nested atomic reaches the bound.
SAB_ID="S95-atomic-trail-uncharged"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness atomicdiff"
SAB_HARNESS_TARGET="tests/atomic_groups/atomic_quant.rxt"
SAB_DESC="vm_cost's A_ATOMIC arm returns the body's Cost without adding the trailed cut mark, so trail_frames is short by one entry per emitted atomic group on the deepest path. Nothing is emitted differently and no answer changes -- the artifact returns PCREC_ERR_FRAMES on a pattern it can match, S87's failure mode one construct over"
SAB_DOC_FIGURE="PREDICTED: the capacity/subject_ceiling assertions RED on a deep-nested atomic; codegen GREEN, because nothing about the emitted code moves. That 0-fail codegen column is the row's point. Canonical figure owed from run_sabotage_matrix.sh S95."
SAB_COUNT=1
SAB_BEFORE='        c = vm_cost(v, a->l, false);
        c.trail += 1;
        return c;'
SAB_AFTER='        c = vm_cost(v, a->l, false);
        return c;   /* SABOTAGE S95: the trailed mark is not charged */'
