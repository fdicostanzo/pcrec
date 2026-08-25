# S145 ([DD-14] wave B+C, design SS9.3 S-SR3) -- THE CALL FRAME IS NOT POPPED
# BY THE RETURN.
#
# THE CLAIM, and it is a MEASURED fact about 10.46 rather than a design
# preference: **the call is BACKTRACKABLE**. PCRE2 was atomic here before
# 10.30 and is not now, so the callee's choice points must survive the return
# and so must the return label they will come back through.
#
# THE OBVIOUS CELL DECIDES NOTHING and the design says so where it states it:
# `^(a|ab)(?1)c$` on "ababc" matches under BOTH hypotheses, because the
# LEXICAL group can retry too. The isolated cell puts the body where only the
# call can reach it:
#
#     ^(?:(?<g>a|ab)){0}(?&g)c$  on "abc"  ->  (0,3)   BACKTRACKABLE
#                                              atomic would be NOMATCH
#
# with FOUR ATOMIC CONTROLS all answering nomatch, which is what makes the row
# above evidence rather than a coincidence.
#
# WHY POPPING IS THE SABOTAGE RATHER THAN CUTTING. Popping the call frame
# discards the ACTIVATION RECORD, which is the thing SS5.2's whole derivation
# is about; cutting discards the callee's frames. The two produce the same
# answer on the discriminator and different answers elsewhere, which is why
# they are two rows (S146 is the cut) and why THIS one's distinguishing mark
# is that a SECOND call after the first returns reads a clobbered stack.
SAB_ID="S145-call-return-pops"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="The emitted return POPS the call frame (\`--run->resume_depth\`) before jumping, so the callee's choice points die with it -- the call becomes ATOMIC, which is 10.30's behaviour and not 10.46's"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR3): the backtrack-into-a-returned-call population goes red. atomicity.rxt's isolated discriminator ^(?:(?<g>a|ab)){0}(?&g)c\$ on \"abc\" answers nomatch where 10.46 answers (0,3)."
SAB_COUNT=1
SAB_BEFORE='        "        const size_t %s_call_frame = run->call_top;\n"'
SAB_AFTER='        "        const unsigned %s_call_frame = run->call_top;\n"
        "        --run->resume_depth;   /* SABOTAGE S145 */\n"'
