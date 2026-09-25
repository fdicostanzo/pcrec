# S275 ([chkgaps] check-design closure) — THE EMITTED FOLD COMPARE'S OWN
# CONSTANT SHIFTED: the fold form's OTHER unsound direction.
#
# WHAT IT BREAKS, AND WHY S228 CANNOT SEE IT. S228 (tests/base/cls_fold.rxt's
# own detector) sabotages `vm_cls_shape`'s RECOGNIZER — the conjuncts that
# decide WHETHER a class takes the fold shape. This row leaves the recognizer
# untouched and sabotages the line that RENDERS the shape once selected
# (`vm_cls_test`, src/gen/emit_vm.c ~1655): `byte, hi` becomes `byte, lo`, so
# the emitted compare reads `(byte | 0x20) == <lo>` instead of `== <hi>`.
#
# `byte | 0x20` always sets bit 0x20; `lo` (an uppercase ASCII letter,
# 'A'..'Z') never has that bit set (that is `vm_cls_shape`'s own recognizer
# condition, unchanged by this plant). So the compare becomes UNSATISFIABLE
# for every fold class in the artifact: the shape's whole 26-pair population
# loses BOTH members at once, everywhere it appears, in one compiler build --
# a complete miscompile of every caseless-letter class the VM emits, with the
# recognizer itself never having done anything wrong.
#
# THE DETECTOR is tests/codegen/run_cls_fold_agreement.sh, on BOTH its halves
# for every one of the 26 real fold-pair witnesses: the STRUCTURAL check
# (which greps the emitted text for the exact `== <hi>` constant) fails
# because the artifact now reads `== <lo>`, and the BEHAVIOURAL check fails
# on both the `lo` and `hi` probes (the compare is now unsatisfiable) while
# the two negative-control probes stay correctly nomatch -- three of each
# pair's five checks fail, 78 of 130 F-population checks total. Every one of
# the 6 near-miss (bitmap-shape) witnesses and SOURCE A's own three checks
# stay green -- the split that names the failure as the EMITTED LINE's, not
# the recognizer's, exactly as S228's own split names the recognizer's
# conjuncts by leaving the fold-PAIR rows green.
SAB_ID="S275-cls-fold-emitted-constant-shifted"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="clsfold"
SAB_DESC="vm_cls_test's FOLD case prints (byte | 0x20) == lo instead of == hi -- an unsatisfiable compare (lo never carries bit 0x20) that loses BOTH members of every ASCII fold-pair class, everywhere the VM class-fold shape fires"
SAB_DOC_FIGURE="MEASURED 2026-09-25 (lane chkgaps, solo single-row scratch run via tests/mech/run_sabotage_matrix.sh S275): DETECTED, reach:ok(1/1), clsfold:78fail/85pass -- all 26 fold-pair witnesses fail their structural shape check plus both their lo/hi behavioural probes (3 of 5 checks each, 78 total), the 6 near-miss (bitmap-shape) witnesses and SOURCE A's own checks stay green. Read the current figure from a run."
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/fp.c" --pattern "([Aa])x" && grep -q "0x20) == 97" "$REACH_TMP/fp.c" && echo REACH-CLS-FOLD-EMIT'
SAB_REACH_EXPECT="REACH-CLS-FOLD-EMIT"
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(b, "(%s | 0x20) == %d", byte, hi);'
SAB_AFTER='        /* SABOTAGE S275: the emitted constant shifted from hi to lo --
         * unsatisfiable, since (byte | 0x20) never equals an uppercase
         * letter. */
        pcrec_sb_printf(b, "(%s | 0x20) == %d", byte, lo);'
