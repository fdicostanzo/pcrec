# S160 ([DD-14] wave B+C, design SS9.3 S-SR12) -- `revdet`'s `A_CALL` ARM
# DECLINES.
#
# THE FAILURE IS A HARD COMPILE ERROR AND THAT IS THE RIGHT ONE, which is what
# makes this row unusual: it asserts a WALL IS REACHED rather than that an
# answer moved. `vm_rev_emit`'s `default:` is a `ctx_fail` reading "internal
# error: bad AST node in the backward walk" -- loud and correct -- and design
# SS4.4a site (7) records that it is now REACHABLE IN A NEW WAY: a call can
# carry a whole SUBTREE into the backward walk rather than a single node.
#
# FIVE ARMS KEEP IT UNREACHABLE and this row sabotages the FIRST of them.
# SS4.4a sites (14)-(18) are `rd_shape`, `rd_reverse`, `pcrec_revdet_first`,
# `rd_alt_disjoint` and `rd_walk`; `rd_shape`'s decline is the one that stops
# `rd_reverse` being CALLED at all, so it is the arm whose removal exercises
# the rest.
#
# AND `rd_node` IS THE MOST PLAUSIBLE-LOOKING WRONG NODE IN THAT FILE, which
# is worth knowing before reading the failure. It is the reversal COPY
# CONSTRUCTOR, `*n = *src` -- a SHALLOW copy of the union -- so an `A_CALL`
# copy would keep a valid-looking `u.call` and a `body` pointer INTO THE
# FORWARD TREE. Nothing about the copy would look wrong. What stops it is
# `rd_reverse`'s own `case A_CALL:` `ctx_fail` firing before the tail
# fallthrough, and this row is what asserts that ordering still holds.
SAB_ID="S160-revdet-reverses-call"
SAB_FILE="src/opt/revdet.c"
SAB_SUITES="harness recursion rungdiff"
# [DD-14 wave B+C] EXPECTED UNDETECTED, and the expectation is CHECKED.
# The sabotage is real and verified applied; this corpus cannot see it
# yet. SAB_DOC_FIGURE above records the measurement and names exactly
# what would have to exist for this row to close. If the matrix ever
# reports NOW DETECTED here, some wave built that witness: re-measure,
# then flip this to DETECTED -- do not delete the row.
SAB_EXPECT=UNDETECTED
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="rd_shape stops declining an A_CALL, so a call-bearing quantifier body is admitted to the reverse-deterministic rung and the reversal walk reaches a node it has no rule for"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR12): vm_rev_emit's default: fires -- \"internal error: bad AST node in the backward walk\" -- a HARD COMPILE ERROR, which is the RIGHT failure. The row asserts the wall is REACHED, not that an answer changed. Design 4.4a records that (7)'s default: is now reachable in a NEW WAY because a call can carry a whole SUBTREE into the backward walk rather than a single node, and that sites (14)-(18) declining is what keeps it a diagnostic rather than a miscompile. || MEASURED UNDETECTED: corpus 0fail/346pass, recdiff 0fail/7pass, rungdiff 0fail/205pass. \`rd_shape\`'s decline is not the arm that keeps the reversal unreachable on this population -- \`rd_reverse\`'s own \`case A_CALL:\` \`ctx_fail\`, \`rd_alt_disjoint\` and \`vm_revdet_fits\` each refuse independently, and no corpus quantifier body carrying a call is otherwise revdet-eligible (the rung wants a unique-iteration body, which a call's all-bytes FIRST set denies). What is owed is a body that WOULD take the rung but for the call; the shipped five-arm decline is unchanged."
SAB_COUNT=1
SAB_BEFORE='        case A_CALL:
            S->ok = false;
            return;'
SAB_AFTER='        case A_CALL:   /* SABOTAGE S160: admit a call to the revdet rung */
            return;'
