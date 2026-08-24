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
SAB_ID="S157-possessify-across-call"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness recursion"
# [DD-14 wave B+C] EXPECTED UNDETECTED, and the expectation is CHECKED.
# The sabotage is real and verified applied; this corpus cannot see it
# yet. SAB_DOC_FIGURE above records the measurement and names exactly
# what would have to exist for this row to close. If the matrix ever
# reports NOW DETECTED here, some wave built that witness: re-measure,
# then flip this to DETECTED -- do not delete the row.
SAB_EXPECT=UNDETECTED
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="BOTH arms that decline a call are removed -- first_of stops widening to every byte and gk_build stops refusing -- so a possessive quantifier over a call-bearing body is admitted onto vm_poss_star, which emits NO empty-iteration guard and NO work charge, and the emitted matcher HANGS"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR9a, D71 item 6): ^(?:(?<g>a?)){0}(?&g)*+\$ HANGS -- emit_vm.c's own comment says vm_poss_star 'PUSHES AND CUTS AT ZERO CONSUMPTION FOREVER, and no work charge fires to stop it', and eng_brep_design 2.2's nullable refusal CANNOT SEE a callee that lives elsewhere in the tree. Scored by tests/harness/run.sh's own run budget. MEASURED on the landed build BEFORE the sabotage: that pattern compiles with RX_VM_STRATS 0x2 -- BACKTRACKING only, no POSSESSIVE bit -- and answers (0,3) on \"aaa\". || MEASURED UNDETECTED at corpus 0fail/346pass EVEN WITH BOTH POSSESSIFY ARMS REMOVED, and the finding is which arm actually stands between the corpus and the hang. \`(?&g)*+\` does NOT go through possessify at all: parse.c desugars the possessive SUFFIX to A_ATOMIC(A_REP(...)) and \`vm_lifts\` routes the cut into the possessive rung -- and \`vm_lifts\` DECLINES on \`vm_nullable(r->l)\`, which for a call is the GRAPH FIXPOINT (S156's arm). So for the user-written spelling the protection is vm_lifts + vm_nullable, not D71 item 6's rung decline; possessify's decline governs the AUTOMATIC possessification of a non-possessive quantifier, whose hang shape this corpus does not contain. The witness cell ^(?:(?<g>a?)){0}(?&g)*+\\$ landed anyway and is MEASURED on the shipped build to take the BACKTRACKING rung (RX_VM_STRATS 0x2, no POSSESSIVE bit)."
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
