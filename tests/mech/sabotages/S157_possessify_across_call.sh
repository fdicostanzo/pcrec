# S157 ([DD-14] wave B+C, design SS9.3 S-SR9a; D71 item 6) -- RUNG ADMISSION
# DECLINES A CALL-BEARING BODY.
#
# A TIMEOUT ROW, and the suite assignment is the whole point: its signal is
# THAT THE PROCESS DID NOT FINISH, not that an answer changed. S-SR11 is the
# only other row in this module with that shape.
#
# WHY THE DECLINE IS A RULING RATHER THAN A PRECAUTION. `vm_poss_star`
# (emit_vm.c) emits NO empty-iteration guard and fires NO work charge, and
# emit_vm.c says so in terms: "routed onto that rung the emitted matcher
# PUSHES AND CUTS AT ZERO CONSUMPTION FOREVER, and no work charge fires to stop
# it. Sabotage row S100's expected result is a TIMEOUT."
#
# WHAT MAKES THAT SAFE TODAY IS A VERDICT COMPUTED OVER THE BODY'S OWN
# SUBTREE. `eng_brep_design.md` SS2.2 refuses to possessify a NULLABLE body at
# all, so the unguarded rung is never reached with one -- and **a call's body
# is somewhere else in the tree**. SS2.2 structurally cannot see it. That is the
# gap D71 item 6 rules on: rung admission declines EVERY call-bearing body,
# now, on every rung, and the non-nullable-only lift through the call-graph
# fixpoint is chartered rather than built.
#
# **THE DECLINE IS A CONJUNCTION AND THIS ROW SABOTAGES BOTH HALVES, WHICH IS
# A CORRECTION TO ITS OWN FIRST VERSION.** That version removed only
# `gk_build`'s `g->ok = false` and scored UNDETECTED at corpus 0fail/346pass,
# because `first_of`'s `A_CALL` arm STILL widens to every byte and is nullable
# -- so the DISJOINTNESS arm of SS2.2's verdict refuses independently and the
# quantifier is not possessified anyway. Removing one of two independent
# refusals proves nothing about either.
#
# So the row now moves BOTH: `first_of` answers an EMPTY, non-nullable first
# set (which lets disjointness hold vacuously) and `gk_build` answers an
# epsilon (which lets the unique-iteration test pass). Each arm's own comment
# says why its shipped answer is not merely conservative but TRUE -- a
# lookaround really does consume nothing, while a call consumes whatever its
# callee consumes, so modelling a call as an epsilon makes a body look
# PREFIX-FREE that is not.
#
# MEASURED ON THE LANDED BUILD, before the sabotage, so the row's own premise
# is checked rather than assumed: `^(?:(?<g>a?)){0}(?&g)*+$` compiles and
# stamps `RX_VM_STRATS 0x2` -- BACKTRACKING only, no POSSESSIVE bit -- and
# answers (0,3) on "aaa". The rung declined, and the stamp is where that is
# visible.
#
# ============================================================================
# [DD-14 WAVE E] THE ROW IS NOW **DETECTED**, AND WHAT CHANGED IS THE WITNESS
# RATHER THAN THE CODE. Wave B+C landed this row expected-UNDETECTED with an
# honest measurement: the corpus scored 0fail/346pass with BOTH possessify
# arms removed, because `(?&g)*+` -- the shape SS9.3 predicted the HANG on --
# never reaches possessify.c at all. parse.c desugars the possessive SUFFIX to
# `A_ATOMIC(A_REP(...))` and `vm_lifts` declines on `vm_nullable`, which for a
# call is the graph fixpoint (S156's arm). So for the user-written possessive
# spelling the protection is vm_lifts + vm_nullable, and this row's two arms
# govern something else.
#
# WHAT THEY GOVERN IS THE **AUTOMATIC** POSSESSIFICATION OF AN ORDINARY
# QUANTIFIER, and the quantifier the sabotage wrongly possessifies is not the
# one over the call. It is the `a?` INSIDE THE CALLEE. Emptying a call's first
# set (`first_of`'s arm) makes whatever FOLLOWS a call site look disjoint from
# the callee's own first bytes, so `pss_verdict` marks the callee's `a?`
# possessive on the strength of a follow it computed from a lie. The
# consequence is not a hang -- it is a DELETED MATCH, this analysis's unsound
# direction.
#
# THE WITNESS, MEASURED BOTH WAYS on 2026-08-24 (clean binary vs. a binary
# with both arms sabotaged, same tree, same flags):
#
#   ^(a?)(?1)+a$   on "a"    clean: MATCH (0,1), group 1 = (0,0)
#                            sabotaged: NOMATCH        <- the detection
#   ^(a?)(?1){2}a$ on "a"    clean: MATCH (0,1)
#                            sabotaged: NOMATCH        <- through a COUNTED
#                                                         quantifier, so a fix
#                                                         that only taught `+`
#                                                         about calls is not
#                                                         enough
#   ^(a?)(?1)*$    on "aaa"  clean: MATCH   sabotaged: MATCH
#                            RX_VM_STRATS 0x2 -> 0x3 and NO ANSWER MOVES
#
# The third line is why the first two had to be found. Possessifying the
# callee's `a?` is HARMLESS wherever nothing after the call needs the `a`
# back; the trailing literal is what makes the backtrack load-bearing.
# libpcre2 10.46 agrees with the clean build on all three (the cells are
# generator-written from the oracle, tests/recursion/quantified.rxt).
#
# THE HANG PREDICTION IS RETIRED, not merely unmet: `vm_poss_star`'s
# guard-free spin is reachable only through the rung this sabotage cannot
# route to, and `vm_lifts`/S156 stands between the corpus and it. This row is
# therefore an ANSWER comparison rather than the timeout row it was written as.
# ============================================================================
SAB_ID="S157-possessify-across-call"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness recursion"
# [DD-14 wave E] DETECTED. Wave B+C wrote: "If the matrix ever reports NOW
# DETECTED here, some wave built that witness: re-measure, then flip this to
# DETECTED -- do not delete the row." Wave E built it, re-measured it both
# ways, and flipped it. The witness is tests/recursion/quantified.rxt's
# ^(a?)(?1)+a$ and ^(a?)(?1){2}a$ on "a" -- ordinary greedy quantifiers whose
# BACKTRACK is load-bearing, which is the property the old witness lacked.
SAB_EXPECT=DETECTED
SAB_HARNESS_TARGET="tests/recursion/quantified.rxt"
SAB_DESC="BOTH arms that decline a call are removed -- first_of stops widening to every byte and gk_build stops refusing -- so the AUTOMATIC possessifier narrows the CALLEE on the strength of a follow computed from an emptied call first-set, and a quantifier INSIDE the callee is made possessive that must be able to back up: ^(a?)(?1)+a\$ on \"a\" goes from (0,1) to NOMATCH"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR9a, D71 item 6): ^(?:(?<g>a?)){0}(?&g)*+\$ HANGS -- emit_vm.c's own comment says vm_poss_star 'PUSHES AND CUTS AT ZERO CONSUMPTION FOREVER, and no work charge fires to stop it', and eng_brep_design 2.2's nullable refusal CANNOT SEE a callee that lives elsewhere in the tree. Scored by tests/harness/run.sh's own run budget. MEASURED on the landed build BEFORE the sabotage: that pattern compiles with RX_VM_STRATS 0x2 -- BACKTRACKING only, no POSSESSIVE bit -- and answers (0,3) on \"aaa\". || MEASURED UNDETECTED at corpus 0fail/346pass EVEN WITH BOTH POSSESSIFY ARMS REMOVED, and the finding is which arm actually stands between the corpus and the hang. \`(?&g)*+\` does NOT go through possessify at all: parse.c desugars the possessive SUFFIX to A_ATOMIC(A_REP(...)) and \`vm_lifts\` routes the cut into the possessive rung -- and \`vm_lifts\` DECLINES on \`vm_nullable(r->l)\`, which for a call is the GRAPH FIXPOINT (S156's arm). So for the user-written spelling the protection is vm_lifts + vm_nullable, not D71 item 6's rung decline; possessify's decline governs the AUTOMATIC possessification of a non-possessive quantifier, whose hang shape this corpus does not contain. The witness cell ^(?:(?<g>a?)){0}(?&g)*+\\$ landed anyway and is MEASURED on the shipped build to take the BACKTRACKING rung (RX_VM_STRATS 0x2, no POSSESSIVE bit). || [WAVE E] CLOSED AS DETECTED. The witness the search had missed is the AUTOMATIC path, not the possessive-suffix one, and the quantifier it wrongly possessifies is the \`a?\` INSIDE THE CALLEE -- made to look prefix-free by an emptied call first-set. MEASURED both ways 2026-08-24: ^(a?)(?1)+a\$ on \"a\" is (0,1) group1=(0,0) clean and NOMATCH sabotaged; ^(a?)(?1){2}a\$ on \"a\" the same through a COUNTED quantifier; ^(a?)(?1)*\$ on \"aaa\" moves RX_VM_STRATS 0x2 -> 0x3 with EVERY ANSWER UNCHANGED, which is why a cell without a trailing literal could never have closed this. The failure is a DELETED MATCH, not the predicted HANG: vm_poss_star is reachable only through the rung this sabotage cannot route to."
SAB_COUNT=1
SAB_BEFORE='    case A_CALL: {
        First r;
        memset(r.f, 0xff, 32);
        r.nullable = true;
        return r;
    }'
SAB_AFTER='    case A_CALL: {   /* SABOTAGE S157: a call has an EMPTY first set */
        First r;
        memset(r.f, 0, 32);
        r.nullable = false;
        return r;
    }'
SAB_FILE2="src/opt/possessify.c"
SAB_COUNT2=1
SAB_BEFORE2='    case A_CALL:
        g->ok = false;
        return gk_parts_empty(true);'
SAB_AFTER2='    case A_CALL:   /* SABOTAGE S157 (second site): modelled as an epsilon */
        return gk_parts_empty(true);'
