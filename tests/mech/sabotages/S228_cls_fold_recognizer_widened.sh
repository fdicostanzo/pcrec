# S228 ([FORM-CHAR] STEP 1) — THE FOLD RECOGNIZER WIDENED TO ANY TWO-MEMBER
# CLASS: the fold form's UNSOUND direction.
#
# RE-ANCHORED 2026-09-30 (lane clss2, [CLS-TREE] S2): `vm_cls_shape` is
# retired; the recognizer is now clskit.c's `is_ascii_fold_pair`, the
# predicate of the `byte-fold` ROWS row the VM spells as the fold compare.
# Same conjuncts dropped, same two-direction miscompile, intent unchanged.
#
# WHAT IT BREAKS. The recognizer gives a class the FOLD
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
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/base/cls_fold.rxt"
SAB_DESC="clskit.c's is_ascii_fold_pair (the byte-fold row's predicate) loses its (lo ^ hi) == 0x20 and letters conjuncts, so ANY two-singleton class takes the ascii-fold compare (byte | 0x20) == hi -- exact for a fold pair, a two-direction miscompile for every other two-member set ([ac] loses 'a' and admits 'C')"
SAB_DOC_FIGURE="MEASURED 2026-09-05 (lane formchar1, at its vm_cls_shape anchor): DETECTED, reach:ok(1/1), corpus:7fail/51pass on tests/base/cls_fold.rxt. Re-anchored 2026-09-30 (clss2); read the current figure from a run."
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/np.c" --pattern "([ac])x" && grep -q "rx_class_bitmap0" "$REACH_TMP/np.c" && "$PCREC" -p rx -o "$REACH_TMP/fp.c" --pattern "([Aa])x" && grep -q "| 0x20) == 97" "$REACH_TMP/fp.c" && grep -q "^#define RX_VM_CLS_FOLDS 1" "$REACH_TMP/fp.c" && echo REACH-CLS-FOLD-BOTH-ARMS'
SAB_REACH_EXPECT="REACH-CLS-FOLD-BOTH-ARMS"
SAB_COUNT=1
SAB_BEFORE='    return n == 2 && iv[0].lo == iv[0].hi && iv[1].lo == iv[1].hi
        && (iv[0].lo ^ iv[1].lo) == 0x20 && iv[0].lo >= '"'"'A'"'"' && iv[0].lo <= '"'"'Z'"'"';'
SAB_AFTER='    /* SABOTAGE S228: the fold recognizer widened to ANY two-singleton
     * class -- (byte | 0x20) == hi admits bytes outside a set that is not
     * a 0x20-pair and loses members whose or-mask misses the constant. */
    return n == 2 && iv[0].lo == iv[0].hi && iv[1].lo == iv[1].hi;'
