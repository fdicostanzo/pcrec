# S169 ([DD-14.LB]) -- THE POST-RESOLUTION PASS IS NEVER CALLED.
#
# THE CLAIM: a lookbehind whose body carries a call is RECORDED by module
# `lookaround`'s parse hook rather than measured there — `pcrec_maxw`'s A_CALL
# arm cannot answer at that timing, because `u.call.body` is bound over the
# FINAL tree and a forward call's target is not parsed yet — and
# `pcrec_postresolve` (src/opt/postresolve.c) re-asks the module's own rule
# after `pcrec_callgraph_build`. Delete the call and the recording half is
# still there while the resolving half is gone.
#
# WHAT THE ARTIFACT DOES, PREDICTED, and it is deliberately NOT a miscompile:
# a recorded lookbehind reaches `vm_look_behind` with `u.look.widths == NULL`,
# which that function already `ctx_fail`s on by name ("the parse hook did not
# run, or its deferred width re-check did not"). So the compile ABORTS with an
# internal error rather than emitting a back-step of width zero. THAT GUARD IS
# HALF OF WHAT THIS ROW MEASURES: the pending state was given the encoding it
# has (`widths == NULL`, the state `vm_look` was ALREADY loud about) precisely
# so that losing this pass could not be silent. A design that had recorded
# "pending" in a new boolean and left `widths` pointing at a zeroed table would
# fail this row as a WRONG SPAN instead, and on a negative lookbehind as a
# FALSE MATCH.
#
# THE DETECTOR IS THE MATCH CELLS AND NOT THE `perr` CELLS. Every `perr` cell
# in the target file still exits nonzero under this sabotage (with a different
# message, which `.rxt`'s `perr` does not read — docs/testing.md), so a row
# scored on those alone would read CLEAN. The seven `m`/`n` blocks are what
# move.
SAB_ID="S169-postresolve-pass-deleted"
SAB_FILE="src/core/compile.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/recursion/inlookaround.rxt"
SAB_DESC="pcrec_postresolve is never called, so a lookbehind recorded by the parse hook (its body carries a call) never has its width table resolved"
SAB_DOC_FIGURE="PREDICTED ([DD-14.LB]): the seven call-bearing-lookbehind MATCH blocks in tests/recursion/inlookaround.rxt fail as PATTERN-COMPILE FAILURES, not as wrong spans -- vm_look_behind ctx_fails on the pending shape. The file's four perr blocks still pass (a perr cell asserts a nonzero exit, not a message), which is why the row is scoped to a file that has match cells at all."
SAB_COUNT=1
SAB_BEFORE='    pcrec_postresolve(&cx, root);'
SAB_AFTER='    (void)0;   /* SABOTAGE S169: pcrec_postresolve(&cx, root); */'
