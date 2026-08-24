# S130 ([M6.6.2] wave B+C, design §9.3 S-LA15) — `.behind` IS READ.
#
# **THIS ROW IS EXPECTED TO SCORE `UNDETECTED` UNTIL WAVE D LANDS, AND THAT IS
# A PROPERTY OF THE WAVE RATHER THAN OF THE ROW.** It is written out now (R33
# C2-8 required all three flag rows written rather than promised), and the
# report for wave B+C states the deferral, so a matrix reader does not take it
# for a finding.
#
# WHY IT CANNOT BE LIVE YET. What `.behind` SELECTS is §3.4's back-step and
# end-check, and neither exists: `pcrec_laport_group` declines the three `(?<`
# tails at `WANT_RESULT`, so no `A_LOOK` with `behind == true` can be built at
# all, and `vm_look`'s only read of the flag today is the LOUD `ctx_fail` this
# row deletes — whose deletion is unobservable precisely because nothing can
# reach it. A sabotage of an unreachable guard is not a detector.
#
# WAVE D OWES THIS ROW A RE-HOMED ANCHOR, not a new row: when the back-step
# lands, `SAB_BEFORE` must move onto the emission that BRANCHES on `.behind`
# (the back-step and the end-check), and the detector becomes
# `lookbehind.rxt` and `startpos.rxt` — every `(?<=`/`(?<!` cell goes red,
# which is design §9.3's stated prediction. Until then the anchor sits on the
# guard so that the row EXISTS, drifts loudly if `vm_look` is rewritten, and
# is impossible to forget.
SAB_ID="S130-look-ignores-behind"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness lookaround"
SAB_HARNESS_TARGET="tests/lookaround"
SAB_DESC="vm_look stops reading Ast.u.look.behind, so a LOOKBEHIND would be emitted with the lookAHEAD shape — no back-step, no end-check. DEFERRED: unobservable until wave D lands the lookbehind, because the parse hook declines the three (?< tails and nothing can build such a node"
SAB_DOC_FIGURE="EXPECTED UNDETECTED AT WAVE B+C, by construction — see this row's header. At wave D the anchor is re-homed onto the back-step/end-check emission and the prediction becomes: every (?<= and (?<! cell in lookbehind.rxt and startpos.rxt goes red."
SAB_COUNT=1
SAB_BEFORE='    if (a->u.look.behind)
        ctx_fail(v->cx, 0, "internal error: a LOOKBEHIND reached vm_look "
                           "before wave D — the back-step is not built");'
SAB_AFTER='    /* SABOTAGE S130: .behind is not read at all */'
