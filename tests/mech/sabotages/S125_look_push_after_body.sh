# S125 ([M6.6.2] wave B+C, design §9.3 S-LA4) — THE FRAME IS PUSHED BEFORE THE
# BODY.
#
# THE CLAIM (design §3.3). A negative lookaround's whole requirement — "if the
# body fails, SUCCEED with the cursor and the captures restored" — is
# discharged by ONE `RX_PUSH`, and only because that push happens BEFORE the
# body runs. `RX_PUSH` records `scan_position` AND `trail_depth` at push time,
# and the fail label restores the first and rewinds to the second before
# jumping. Push it anywhere later and the frame carries a trail mark taken
# after the body has already written, so a rewind to it does not undo the
# body's captures.
#
# WHAT THIS ROW ACTUALLY DOES, stated exactly rather than as the design's
# sketch. Moving the `vm_push` CALL after `vm_emit` moves the emitted
# `RX_PUSH` STATEMENT after the body's emitted code, where nothing branches to
# it — so the frame is never pushed at all and the negative form can never
# succeed. That is a COARSER signal than the design sketched (which predicted
# `(?!(a)x)ab` reporting g1=(0,1) instead of unset), and it is the honest one:
# in the landed shape a stale-trail-mark push is not expressible as a text
# substitution, because the push and the body emission are two calls whose
# ORDER is the whole mechanism. The claim defended is the same one — the
# push's placement relative to the body — and the direction is safe: this
# sabotage cannot be repaired by anything downstream.
SAB_ID="S125-look-push-after-body"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness lookaround"
SAB_HARNESS_TARGET="tests/lookaround"
SAB_DESC="vm_look emits the negative form's body-failed RX_PUSH after the body instead of before it, so the frame that carries the entry cursor and trail mark is never reached and a negative assertion can never hold"
SAB_DOC_FIGURE="PREDICTED: every negative cell goes red, AHEAD AND BEHIND since wave D — the assertion never succeeds — while every positive and non-atomic cell stays green. Canonical figure owed from run_sabotage_matrix.sh S125."
SAB_COUNT=1
# ANCHOR RE-HOMED AT WAVE D, not rewritten: `vm_look` gained the lookbehind's
# branch chain, so the body emission is no longer a bare `vm_emit` call — it is
# an `if (behind)` whose two arms both end at `okl`. Site 2 therefore anchors
# on the `okl` label emission that follows BOTH arms, which is where "after the
# body" now is for a lookahead AND for a lookbehind; the row's intent is
# unchanged and is now exercised on six spellings instead of three.
SAB_BEFORE='    if (neg)
        vm_push(v, negokl, "negative lookaround: the BODY-FAILED continuation "
                           "-- reaching it means the assertion HOLDS");'
SAB_AFTER='    /* SABOTAGE S125: the push moved AFTER the body emission below */'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='    if (neg) {
        vm_lbl(v, okl, "negative lookaround: the body SUCCEEDED, so the "'
SAB_AFTER2='    if (neg)
        vm_push(v, negokl, "negative lookaround: the BODY-FAILED continuation "
                           "-- reaching it means the assertion HOLDS");
    if (neg) {
        vm_lbl(v, okl, "negative lookaround: the body SUCCEEDED, so the "'
