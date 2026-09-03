# S225 ([OPT-VMFL] STEP 0, r51fix item 3) — THE `RX_VM_FRAMELESS` STAMP IS
# RECOMPUTED FROM `v.npush` INSTEAD OF READING THE HOISTED `has_push` BOOL.
#
# WHAT IT BREAKS. `src/gen/emit_vm.c`'s own comment beside `has_push`
# ("[CC-CLANG fix, 2026-09-01] has_push is NO LONGER computed here from
# v.npush") names this exact derivation and rejects it BY NAME: `v.npush` is
# `vm_count_slots`'s pre-pass push-site COUNT, whose original consumer is the
# resume-point cap, "where an error is an accounting bug" -- not a fact about
# whether the dispatch is reachable. Two independent reasons make it the
# wrong source. (1) It is an ESTIMATE: the counter rung's unbounded arm was
# MEASURED to drive it NEGATIVE, which under this derivation would read
# `> 0` false and omit the dispatch from a program that still pushes ten
# times. (2) `vm_count_slots`'s own `A_CALL` arm deliberately does NOT count
# a linked call SITE toward `npush` ("the call site itself allocates
# nothing", because a call frame is not a SLOT) -- but `RX_CALL` still
# increments `run->resume_depth` at run time, so "a call-only program can
# push despite npush == 0" is the file's own recorded fact, and this plant
# reads that exact zero as FRAMELESS.
#
# THE FAILURE MODE IS THE SAME QUIET KIND AS S224's, from the OTHER
# direction: a program that genuinely pushes (a linked call with no other
# choice point, or the counter rung's negative-estimate case) stamps
# FRAMELESS 1 while the fail label's own dispatch -- written from has_push
# directly, unaffected by this plant -- is still emitted. The stamp then
# claims no resume mechanism exists on an artifact that has one; again no
# ANSWER moves, only the fact a bench or dlopen consumer reads through the
# stamp.
#
# THIS ROW AND S224 ARE THE TWO ROWS THE r51 PANEL FOUND MISSING (finding 3).
SAB_ID="S225-vm-frameless-stamp-from-npush"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="vmframeless"
SAB_DESC="The RX_VM_FRAMELESS stamp is recomputed from v.npush (the resume-point cap pre-pass ESTIMATE) instead of reading the hoisted has_push bool (v.emitted_push || v.has_linked_calls) -- the exact derivation the emitter own comment rejects by name. v.npush excludes a linked call site own frame by design and was MEASURED driven negative by the counter rung unbounded arm, so a program that genuinely pushes (a call-only program, or the negative-estimate case) stamps FRAMELESS 1 while the fail label dispatch, written from has_push directly at a separate site, is still emitted"
SAB_DOC_FIGURE="MEASURED 2026-09-03 (r51fix item 3, solo mech run, tree 26644f50edcafbceb056616650f6cca2f80f4d89): DETECTED, unexpected: 0 -- reach:ok(1/1), vmframeless:1fail/5pass. One check goes red in section3's corpus sweep, on the population where a VM artifact's real goto* dispatch disagrees with the npush-derived stamp (a linked call with no other push site, npush == 0, has_push true) -- confirming the row is narrow but real, and that no answer moves anywhere else in the tree."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree a
# linked-recursive-call witness compiles to a VM program, reaches BOTH the
# has_push definition and the npush pre-pass count, and correctly stamps
# FRAMELESS 0 (it pushes) on the default axis.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" -- "^(a(?1)?b)$" && grep -q "^    goto rx_L0;" "$REACH_TMP/o.c" && grep -q "^#define RX_VM_FRAMELESS 0" "$REACH_TMP/o.c" && echo REACH-LINKED-CALL-PUSHES'
SAB_REACH_EXPECT="REACH-LINKED-CALL-PUSHES"
SAB_COUNT=1
SAB_BEFORE='    sb_printf(c, "#define %s_VM_FRAMELESS %d\n", v.up, has_push ? 0 : 1);'
SAB_AFTER='    /* SABOTAGE S225: the stamp is recomputed from v.npush instead of
     * has_push -- the derivation the emitter own [CC-CLANG fix] comment
     * rejects by name, because npush is a resume-point-cap ESTIMATE (can go
     * negative) that also excludes a linked call site own frame by design. */
    sb_printf(c, "#define %s_VM_FRAMELESS %d\n", v.up, v.npush > 0 ? 0 : 1);'
