# S146 ([DD-14] wave B+C, design SS9.3 S-SR4) -- THE RETURN DOES NOT CUT.
#
# THE CLAIM is S145's, approached from the other side, and the PAIR is what
# makes either row informative. Design SS3.2 MEASURED that the call is
# backtrackable on 10.46 with FOUR ATOMIC CONTROLS refusing:
#
#     ^(?(DEFINE)(?<g>a|ab))(?&g)c$        (0,3)   backtrackable
#     an atomic callee body   (?>a|ab)     nomatch
#     an atomic wrapper       (?>(?&g))    nomatch
#     a possessive call       (?&g)++      nomatch
#     an atomic wrapper round a giving-back callee   nomatch
#
# so "the call retries" and "the four controls do not" are two independent
# facts, and a compiler that cut at the return gets the first wrong while
# still getting the second RIGHT.
#
# THAT IS THIS ROW'S SIGNATURE AND IT IS THE REASON IT IS NOT S145. Under
# S145 (the return pops the frame) the activation record is gone and the
# failure spreads into SS5.2's clobber territory; under this one the record
# survives and only the CHOICE POINTS die, so the four atomic controls stay
# GREEN and the discriminator alone goes red. A matrix that showed both rows
# red in the same population would not have told those apart.
#
# `RX_CUT` IS NOT USED BY THIS MODULE AT ALL, which design SS6.6 records in
# its reuse inventory under "NOT USED" with the reason: the plan row offered a
# cut at the return as the alternative and SS3.2 measured it wrong for 10.46.
# The sabotage therefore has to WRITE the cut rather than delete one, which is
# why its AFTER is longer than its BEFORE.
SAB_ID="S146-call-return-cuts"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="The emitted return CUTS the resume stack back to the call frame, making every subroutine call ATOMIC -- 10.30's semantics, which 10.46 abandoned"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR4): the same cell S145 names goes red, AND THE FOUR ATOMIC CONTROLS STAY GREEN -- which is what distinguishes this row from S145. atomicity.rxt carries both halves."
SAB_COUNT=1
SAB_BEFORE='        "        run->call_top = run->resume_stack[%s_call_frame].call_top;\n"'
SAB_AFTER='        "        run->resume_depth = %s_call_frame;   /* SABOTAGE S146 */\n"
        "        run->call_top = run->resume_stack[%s_call_frame].call_top;\n"'
