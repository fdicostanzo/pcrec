# S103 (design row S-BR15) — PUBLISH-AT-OPEN RESTORED.
#
# R32 E1 EXACTLY, as a row. `A_CAP` used to WRITE ON TRAVERSE: the start slot
# at the opening position, the end slot at the closing one. On iteration n > 1
# of a quantified group that leaves start = iteration n's and end = iteration
# n-1's — NEITHER `PCREC_UNSET`, so a backreference's "is it set" test passes
# on a pair that is NOT A CAPTURE.
#
# TWO FAILURE MODES, and the second is worse. `(a|b\1)+` on "ab" is libpcre2
# (0,1) with group 1 = (0,1) and the write-on-traverse model answers (0,2)
# with group 1 = (1,2) — a wrong answer. `^(?:(a|b\1)y)+` on "aybay" gives
# ref_start = 2 > ref_end = 1, so the emitted `(size_t)(ref_end - ref_start)`
# UNDERFLOWS to SIZE_MAX and the compare reads out of bounds: K27's class, in
# EMITTED code, in a matcher someone else compiles.
#
# WHAT CATCHES IT is `selfref.rxt`'s re-entry cells and `run_backref_diff.sh`
# §3 — and NOTHING ELSE CAN. A 5,808-cell arm-vs-arm sweep found the
# backref-FREE control population at 0 divergences in BOTH publication
# disciplines: publication is unobservable without a backreference, because at
# match completion every group is closed.
SAB_ID="S103-publish-at-open"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="brefdiff dupnamesdiff harness"
SAB_HARNESS_TARGET="tests/backrefs"
SAB_DESC="A_CAP's emission writes the START slot at the opening position again instead of a per-group PENDING slot, so a re-entered group holds a HALF-OPEN pair that a backreference reads as a capture. (a|b\\1)+ on \"ab\" answers (0,2) g1=(1,2) where libpcre2 says (0,1) g1=(0,1), and ^(?:(a|b\\1)y)+ on \"aybay\" underflows a size_t in the emitted compare"
SAB_DOC_FIGURE="PREDICTED: brefdiff RED (§1 span AND group-span cells, §3's population); the backrefs corpus RED on selfref.rxt's re-entry block. Canonical figure owed from run_sabotage_matrix.sh S103."
SAB_COUNT=1
SAB_BEFORE='            if (marked)
                vm_set(v, vm_slot_pend(v, a->u.cap.no), "(ptrdiff_t)scan_position",'
SAB_AFTER='            if (0)   /* SABOTAGE S103: publish at OPEN, as before R32 E1 */
                vm_set(v, vm_slot_pend(v, a->u.cap.no), "(ptrdiff_t)scan_position",'
