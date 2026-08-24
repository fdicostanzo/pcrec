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
# THE ARM SABOTAGED IS `gk_build`'s, and it is the one that DECIDES rather than
# the one that describes. `first_of`'s `A_CALL` arm widens to all bytes and
# `pss_walk`'s declines to descend; either alone would still leave the other
# two to refuse. `gk_build` sets `g->ok = false`, which is the verdict the
# unique-iteration test reads, and its own comment says why an epsilon would be
# a LIE where it is merely conservative for a lookaround: a lookaround really
# does consume nothing, while a call consumes whatever its callee consumes, so
# modelling it as an epsilon makes a body look PREFIX-FREE that is not.
#
# MEASURED ON THE LANDED BUILD, before the sabotage, so the row's own premise
# is checked rather than assumed: `^(?:(?<g>a?)){0}(?&g)*+$` compiles and
# stamps `RX_VM_STRATS 0x2` -- BACKTRACKING only, no POSSESSIVE bit -- and
# answers (0,3) on "aaa". The rung declined, and the stamp is where that is
# visible.
SAB_ID="S157-possessify-across-call"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="timeout recursion"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="gk_build stops declining an A_CALL, so the unique-iteration walk models a call as a zero-width epsilon and a possessive quantifier over a call-bearing body is admitted onto vm_poss_star -- which emits NO empty-iteration guard and NO work charge, so the emitted matcher HANGS"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR9a, and D71 item 6): a TIMEOUT row like S-SR11, not an answer comparison. ^(?:(?<g>a?)){0}(?&g)*+\$ hangs -- vm_poss_star emits no empty-iteration guard and fires no work charge (emit_vm.c's own comment, whose sabotage row S100 also expects a TIMEOUT), and eng_brep_design 2.2's nullable refusal CANNOT SEE a callee that lives elsewhere in the tree. MEASURED on the landed build before the sabotage: that pattern compiles with RX_VM_STRATS 0x2 (BACKTRACKING only, no POSSESSIVE bit) and answers (0,3) on \"aaa\"."
SAB_COUNT=1
SAB_BEFORE='    case A_CALL:
        g->ok = false;
        return gk_parts_empty(true);'
SAB_AFTER='    case A_CALL:   /* SABOTAGE S157: a call is modelled as an epsilon */
        return gk_parts_empty(true);'
