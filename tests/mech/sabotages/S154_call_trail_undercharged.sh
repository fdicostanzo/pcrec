# S154 ([DD-14] wave B+C, design SS9.3 S-SR7) -- `vm_cost` CHARGES `2*|W|`
# TRAIL ENTRIES PER CALL, NOT `|W|`.
#
# THE COST IS TWO PER SLOT AND THE TWO ARE DIFFERENT WRITES. At the call site
# each slot in `W` gets a TRAILED SELF-WRITE, which parks the caller's value on
# the trail; at the region's exit each gets a TRAILED RESTORE, which puts it
# back. Both go through `RX_SET`, so both consume a trail entry, and the total
# is a compile-time constant the capacity analysis has to see.
#
# THE FAILURE MODE IS A WRONG ANSWER ON A PATTERN THAT MATCHES, which is why
# this row exists at all: an artifact whose `trail_frames` is sized from a
# halved charge returns `PCREC_ERR_FRAMES` on a subject the pattern can match.
# That is S87's and S95's exact shape one construct over -- an uncharged
# trailed write sizing the array short -- and it is the direction D22 rules
# out, because a give-up is only honest when the bound is the real one.
#
# NO ANSWER CHANGES UNTIL THE TRAIL IS EXHAUSTED, and that is what makes the
# detector unusual. A corpus cell has to pick a subject LENGTH in advance, so
# it can only see the halved charge if the length it picked happens to cross
# the new, lower ceiling. `run_recursion_diff.sh` SS2 does the honest thing
# instead: it BISECTS for the artifact's own ceiling on `^(a(?1)?b)$` over
# a^n b^n and asserts that one step past it the answer is a typed GIVE-UP
# rather than a `nomatch` -- a property that holds at whatever the ceiling is
# and fails the moment the declared capacity and the real one disagree.
#
# THE DESIGN CALLS THIS A TWO-SITE ROW, and under this implementation it is
# ONE. SS9.3's reason for two was that "the cost arm and the emission must move
# together or the artifact declares a capacity it does not use" -- and here the
# EMISSION is driven from `u.call.nsave`, the same field the cost arm reads,
# so there is exactly one number and no second site to keep in step. That is a
# property of the implementation rather than of the design, and it is recorded
# here because the design's own count is otherwise the thing a reader would
# check against.
SAB_ID="S154-call-trail-undercharged"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion codegen"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="vm_cost charges |W| trail entries per call instead of 2*|W|, so the artifact declares a trail capacity it does not have and answers PCREC_ERR_FRAMES on a pattern it can MATCH -- S87/S95's exact failure mode"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR7): NO ANSWER CHANGES until the trail is exhausted, then PCREC_ERR_FRAMES on a matching subject. The detector is therefore a DEEP-CALL cell rather than a corpus answer, which is what run_recursion_diff.sh's 2 bisection provides: it finds the artifact's own ceiling and asserts that ONE STEP BEYOND IT the answer is a typed give-up rather than a wrong nomatch. The corpus arm is assigned too because a halved charge shrinks the ceiling far enough that leftrec.rxt's 200-deep cell can cross it."
SAB_COUNT=1
SAB_BEFORE='        c.trail  += 2LL * a->u.call.nsave;'
SAB_AFTER='        c.trail  += 1LL * a->u.call.nsave;   /* SABOTAGE S154 */'
