# S226 ([OPT-VMFL] STEP 0, r51fix item 3) — THE `RX_VM_FRAMELESS` STAMP IS
# EMITTED CONDITIONALLY: ONLY FOR A FRAMELESS PROGRAM.
#
# WHAT IT BREAKS. The macro spec section6.3 family (b) rule is UNCONDITIONAL
# on every VM artifact, hybrids included: the file own comment states this
# explicitly ("A fact readable by a macro ABSENCE is the discriminator
# [DD-13] had to go back and remove from two checks, [OPT-1] own
# _FAST_FRAMES precedent"). This plant wraps the `sb_printf` call in
# `if (!has_push) { ... }`, so a PUSHING program emits NO
# RX_VM_FRAMELESS macro at all -- the fact becomes readable only by the
# macro ABSENCE, exactly the shape the file own comment names as the wrong
# one.
#
# WHY THIS IS ITS OWN ROW AND NOT A SECOND HUNK OF S224 (r51fix item 3's
# ruling): the review asked whether the same DETECTOR LINE catches this
# plant and S224's inverted-value plant, and it does not. S224 is caught by
# section1's VALUE-MISMATCH assertion (`[ "$got" = "$want" ] || bad
# "...stamps RX_VM_FRAMELESS $got, expected $want"`) and by section3's
# BICONDITIONAL-VALUE check (`case "$val" in 0|1 ...` then the goto* agreement
# test). This plant instead trips section1's ABSENCE assertion
# (`[ -n "$got" ] || bad "...defines NO RX_VM_FRAMELESS..."`) and section3's
# EXACT-COUNT assertion (`[ "$n" -eq 1 ] || bad "...appears $n times..."`) --
# four different bad() call sites, none shared with S224's two. A row folded
# into S224 would leave one of the two plants' failing directions
# unexercised by anything this row's own header could point to.
#
# THE FAILURE MODE IS AGAIN QUIET: no ANSWER moves, because the fail label
# dispatch itself is written from has_push directly at its own separate
# site, unaffected by whether the STAMP is present. What is lost is
# observability on exactly the population S224/S225 corrupt the VALUE of --
# here the macro is simply gone.
SAB_ID="S226-vm-frameless-stamp-conditional"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="vmframeless"
SAB_DESC="The RX_VM_FRAMELESS macro is emitted CONDITIONALLY -- wrapped in if (!has_push) -- instead of unconditionally on every VM artifact as spec section6.3 requires. A pushing program (has_push true) then defines NO RX_VM_FRAMELESS macro at all: the fact is readable only by the macro ABSENCE, which is the discriminator the file own comment names as the wrong shape ([OPT-1] _FAST_FRAMES precedent). No answer moves -- the fail label dispatch is written from has_push directly, at a separate site unaffected by this plant"
SAB_DOC_FIGURE="PREDICTED (the canonical DETECTED figure is owed from the manager's own matrix run): vmframeless RED in section1 on every want=0 (pushing) named witness (\"is a VM artifact and defines NO RX_VM_FRAMELESS\") and in section3's corpus sweep (\"RX_VM_FRAMELESS appears 0 times on a VM artifact\") on the whole PUSHING population, both axes. corpus:0fail expected -- no answer moves."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree a
# linked-recursive-call (pushing) witness compiles to a VM program and
# stamps RX_VM_FRAMELESS 0 UNCONDITIONALLY -- the macro is present on a
# pushing artifact on the default axis, which is exactly the population
# this plant makes vanish.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" -- "^(a(?1)?b)$" && grep -q "^    goto rx_L0;" "$REACH_TMP/o.c" && grep -q "^#define RX_VM_FRAMELESS 0" "$REACH_TMP/o.c" && echo REACH-PUSHING-STAMP-PRESENT'
SAB_REACH_EXPECT="REACH-PUSHING-STAMP-PRESENT"
SAB_COUNT=1
SAB_BEFORE='    sb_printf(c, "#define %s_VM_FRAMELESS %d\n", v.up, has_push ? 0 : 1);'
SAB_AFTER='    /* SABOTAGE S226: the stamp is emitted CONDITIONALLY -- only for a
     * frameless program -- instead of unconditionally on every VM artifact
     * as spec section6.3 requires. A pushing artifact then defines NO
     * RX_VM_FRAMELESS at all. */
    if (!has_push) {
        sb_printf(c, "#define %s_VM_FRAMELESS %d\n", v.up, 1);
    }'
