# S228 ([FORM-CHAR] STEP 1) — THE FOLD RECOGNIZER WIDENED TO ANY TWO-MEMBER
# CLASS: the fold form's UNSOUND direction.
#
# WHAT IT BREAKS. `vm_cls_shape` (src/gen/emit_vm.c) gives a class the FOLD
# shape only when the set is exactly an ASCII fold pair — two members
# differing only in bit 0x20, both letters — because `(byte | 0x20) ==
# (lo | 0x20)` is exact for PRECISELY the set {lo, lo|0x20} and nothing
# else. This plant drops the pair-and-letters conjuncts, so ANY two-member
# class takes the fold compare: `[ac]` emits `(byte | 0x20) == 'c'`, which
# LOSES 'a' (0x61|0x20 != 0x63) and ADMITS 'C' (0x43|0x20 == 0x63) — a
# miscompile in both directions, in EMITTED code.
#
# THE DETECTOR is tests/base/cls_fold.rxt's `fold-control-nonpair` and
# `fold-and-nonpair-mixed` blocks — capture-bearing patterns (so the default
# compile routes to the VM, the one engine the fold form reaches) whose
# two-member class is NOT a 0x20-pair. Under the plant `([ac])x` on "ax"
# answers nomatch where python3 `re` and the clean build answer (0,2). The
# fold-PAIR blocks in the same file stay green under the plant, which is the
# split that names the failure as the recognizer's, not the compare's. (The
# admit direction, 'C' passing the class, is masked on some artifacts by the
# hybrid's DFA prefilter — emit_dfa.c's class machinery does not read
# `vm_cls_shape` — which is why the detector cells lean on the LOST match.)
SAB_ID="S228-cls-fold-recognizer-widened"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/base/cls_fold.rxt"
SAB_DESC="vm_cls_shape's FOLD arm loses its (lo ^ hi) == 0x20 and letters conjuncts, so ANY two-member class takes the ascii-fold compare (byte | 0x20) == lower — exact for a fold pair, a two-direction miscompile for every other two-member set ([ac] loses 'a' and admits 'C')"
SAB_DOC_FIGURE="MEASURED 2026-09-05 (lane formchar1, solo single-row mech run at the row's landing): DETECTED — harness 6fail/52pass on tests/base/cls_fold.rxt, the fold-control-nonpair and fold-and-nonpair-mixed blocks' match cells (the lost-match direction), with every fold-PAIR block green. Read the current figure from a run."
# [MECH-REACH] the probe says BOTH sides of the recognizer still answer on a
# CLEAN tree: a nonpair two-member class keeps its bitmap (the conjunct this
# plant deletes is live), and a fold pair takes the fold compare and stamps
# it (the arm the plant widens is live).
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/np.c" -- "([ac])x" && grep -q "rx_class_bitmap0" "$REACH_TMP/np.c" && "$PCREC" -p rx -o "$REACH_TMP/fp.c" -- "([Aa])x" && grep -q "| 0x20) == 97" "$REACH_TMP/fp.c" && grep -q "^#define RX_VM_CLS_FOLDS 1" "$REACH_TMP/fp.c" && echo REACH-CLS-FOLD-BOTH-ARMS'
SAB_REACH_EXPECT="REACH-CLS-FOLD-BOTH-ARMS"
SAB_COUNT=1
SAB_BEFORE='    if (count == 2 && (lo ^ hi) == 0x20 && lo >= '"'"'A'"'"' && lo <= '"'"'Z'"'"'
        && !(v->cx->opt->flags & PCREC_NO_CLS_FOLD))
        return VM_CLS_SHAPE_FOLD;'
SAB_AFTER='    /* SABOTAGE S228: the fold recognizer widened to ANY two-member
     * class -- (byte | 0x20) == lower admits bytes outside a set that is
     * not a 0x20-pair and loses members whose or-mask misses the compare
     * constant: the fold form'"'"'s unsound direction, both ways at once. */
    if (count == 2
        && !(v->cx->opt->flags & PCREC_NO_CLS_FOLD))
        return VM_CLS_SHAPE_FOLD;'
