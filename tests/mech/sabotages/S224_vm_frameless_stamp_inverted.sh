# S224 ([OPT-VMFL] STEP 0, r51fix item 3) — THE `RX_VM_FRAMELESS` STAMP'S
# VALUE IS INVERTED AT ITS DEFINITION SITE.
#
# WHAT IT BREAKS. `src/gen/emit_vm.c` computes `has_push` once (`const bool
# has_push = v.emitted_push || v.has_linked_calls;`) and writes the stamp
# from it in the very next statement: `has_push ? 0 : 1`. This plant swaps
# the arms, so a PUSHING program (which needs the fail label's pop-and-resume
# `goto *` dispatch) stamps FRAMELESS 1, and a genuinely FRAMELESS program
# (whose dispatch is OMITTED because clang refuses an indirect goto in a
# function with no address-of-label expression — [CC-CLANG]) stamps
# FRAMELESS 0.
#
# THE FAILURE MODE IS A STAMP THAT LIES ABOUT THE ARTIFACT, exactly
# `tests/codegen/run_search_pinned.sh` S222's shape one construct over: no
# ANSWER moves anywhere in the tree, because the dispatch itself is written
# from `has_push` directly at its own emission site (a SEPARATE write, not
# read back from this stamp) — so the `.rxt` corpus, every oracle and every
# differential stay green. What moves is a fact a BENCH bucketing on the
# stamp, or a `dlopen` consumer reading it through `rx_info`'s own family,
# would act on: told a pushing program has no resume mechanism, or a
# frameless one does.
#
# THIS ROW AND S225 ARE THE TWO ROWS THE r51 PANEL FOUND MISSING (finding 3):
# run_vm_frameless.sh shipped with the three failing directions in its own
# footer "exercised by hand rather than by a permanent mech row" — this is
# the first of them made permanent.
SAB_ID="S224-vm-frameless-stamp-inverted"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="vmframeless"
SAB_DESC="The RX_VM_FRAMELESS stamp's value is written has_push ? 1 : 0 instead of has_push ? 0 : 1 -- the two arms swapped at the pcrec_sb_stampf call, so a PUSHING program (needs the fail label's dispatch) stamps FRAMELESS 1 and a FRAMELESS program stamps FRAMELESS 0. No answer moves: the fail label's own dispatch omission is written from has_push directly at a separate emission site, unaffected by this stamp"
SAB_DOC_FIGURE="MEASURED 2026-09-19 (adm71 item 2, solo mech run, tree d5ea41a7903417dd6c321e3443340423efdbe42f): DETECTED, unexpected: 0 -- reach:ok(1/1), vmframeless:7fail/4pass. UNCHANGED from the 2026-09-03 figure -- the split is arithmetic, not incidental, and holds regardless of the suite's own top-level check count moving over time (six outcome points on a CLEAN run today: the §1 six-witness summary, the §1 negative control, §2's pure-DFA IFF half, the §3 corpus-sweep aggregate, and the two per-axis §3 population floors). The inversion is a BIJECTION on {0,1}, so it wrongly flips ALL SIX §1 named witnesses individually (each prints its own FAIL line from inside witness(), bypassing what would have been ONE aggregate ok() at line 148) plus the §3 corpus-sweep aggregate -- 7 bad() calls where a clean run would print 2 ok()s. The remaining 4 passes are unaffected by construction: §1's negative control and the two §3 per-axis floors read the (still-inverted, still bijective) population sizes, which do not collapse; §2's pure-DFA IFF is untouched because the sabotaged stamp write lives inside emit_vm.c's VM-only path and is never reached for a --no-captures pure-DFA artifact. Confirms detection still holds through §1's per-witness value-mismatch assertions and §3's corpus sweep, no answer moves anywhere else in the tree."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree a
# capture-bearing straight-line pattern compiles to a VM program and stamps
# RX_VM_FRAMELESS 1 -- the has_push definition and the stamp write both
# execute on this witness, on the default axis.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(a)b" && grep -q "^    goto rx_L0;" "$REACH_TMP/o.c" && grep -q "^#define RX_VM_FRAMELESS 1" "$REACH_TMP/o.c" && echo REACH-FRAMELESS-STAMP-CORRECT'
SAB_REACH_EXPECT="REACH-FRAMELESS-STAMP-CORRECT"
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_stampf(c, v->up, "VM_FRAMELESS", "%d", v->has_push ? 0 : 1);'
SAB_AFTER='    /* SABOTAGE S224: the stamp two arms are swapped -- a pushing
     * program now reads FRAMELESS 1 and a frameless one reads FRAMELESS 0.
     * No answer moves; the fail label dispatch omission below is written
     * from has_push directly, at its own separate site. */
    pcrec_sb_stampf(c, v->up, "VM_FRAMELESS", "%d", v->has_push ? 1 : 0);'
